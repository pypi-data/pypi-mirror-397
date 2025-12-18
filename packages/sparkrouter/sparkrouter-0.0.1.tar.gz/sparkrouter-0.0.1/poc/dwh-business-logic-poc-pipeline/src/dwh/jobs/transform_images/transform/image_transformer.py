from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, expr, when, lower, lit, count, struct
from pyspark.sql.types import StringType, StructField, StructType
from pyspark.sql.functions import lit as spark_lit, sum as spark_sum
# from dwh.services.schema.schema_service import SchemaService


class ImageTransformer:
    """
    Image transformer using Scala UDF for high-performance parallel decryption.

    This implementation delegates decryption to a Scala UDF that runs directly
    on executors, enabling parallel processing across the cluster. This is
    critical for processing millions of records with unique encrypted values.

    Prerequisites:
        - decryption-udfs_2.12-1.0.0.jar must be in spark.jars config
        - platform.infrastructure JAR must be in spark.jars config
        - UDF must be registered before calling transform()

    Example setup:
        spark = SparkSession.builder \\
            .config("spark.jars", "jars/decryption-udfs_2.12-1.0.0.jar,jars/platform.infrastructure-1.19.5-SNAPSHOT.jar") \\
            .getOrCreate()

        # Register the Scala UDF
        ImageTransformer.register_udfs(spark)

        # Use transformer
        transformer = ImageTransformer(schema_service, spark)
        result = transformer.transform(df, created_by)
    """

    # Schema for the Scala UDF return type
    DECRYPT_SCHEMA = StructType([
        StructField("msp", StringType(), True),
        StructField("mspid", StringType(), True),
        StructField("mediaid", StringType(), True),
        StructField("locationspec", StringType(), True)
    ])

    @staticmethod
    def register_udfs(spark: SparkSession) -> None:
        """
        Register Scala UDFs with Spark.
        Call this once after SparkSession creation.

        Args:
            spark: Active SparkSession with JARs configured
        """
        # Register the combined decrypt-and-parse UDF
        # This returns a struct with (msp, mspid, mediaid, locationspec)
        spark.udf.registerJavaFunction(
            "decrypt_and_parse",
            "com.yourcompany.udfs.DecryptAndParseUDF",
            ImageTransformer.DECRYPT_SCHEMA
        )

        # Also register simple decrypt for ad-hoc use
        spark.udf.registerJavaFunction(
            "decrypt_value",
            "com.yourcompany.udfs.DecryptUDF",
            StringType()
        )

        print("Registered Scala decryption UDFs")

    def transform(self, df: DataFrame, created_by: str, metrics=None, cache_threshold: int = 10000) -> tuple[DataFrame, DataFrame]:
        """
        Transform incoming nested structure to outgoing format.

        Uses Scala UDF for parallel decryption across executors.
        Tracks records lost due to UDF failures/exceptions.

        PERFORMANCE OPTIMIZATIONS:
        1. Cache df_with_fields (after UDF) since it's used for metrics + 2 filters
        2. Combined aggregation: metrics + data_type distribution in ONE query
        3. Removed useless input df caching (was cached but only used once)

        Args:
            df: Input DataFrame with nested data.* structure
            created_by: Identifier for audit purposes
            metrics: Optional metrics collector
            cache_threshold: Only cache if record count >= threshold (default: 10000)
                           For small datasets, caching overhead > re-execution cost

        Returns:
            Tuple of (valid_df, dropped_df)
            - valid_df: Successfully transformed records
            - dropped_df: Records that failed transformation (with drop_reason)
        """
        # Get input count from metrics (avoid count() action)
        if metrics and hasattr(metrics, 'extract_records_after_filter') and metrics.extract_records_after_filter is not None:
            input_count = metrics.extract_records_after_filter
            print(f"[TRANSFORM] Starting with {input_count} records (from extract metrics)")
        else:
            # Fallback only if metrics not available - this triggers a scan
            input_count = df.count()
            print(f"[TRANSFORM] Starting with {input_count} records (counted - metrics unavailable)")

        if metrics:
            metrics.transform_records_input = input_count

        # NOTE: We do NOT cache input df here - it's only used once for transformation
        # Caching it would waste memory since we immediately transform it

        df_flattened = df.select(
            col("data.projectguid").alias("projectguid"),
            col("data.project_type").alias("project_type"),
            col("data.project_subtype").alias("project_subtype"),
            col("data.userid").alias("userid"),
            col("data.inserted").alias("inserted"),
            col("data.updated").alias("updated"),
            col("data.product_index").alias("product_index"),
            col("data.product_type").alias("product_type"),
            col("data.productguid").alias("productguid"),
            col("data.productimageid").alias("productimageid"),
            col("data.image_view").alias("image_view"),
            col("data.image_id").alias("image_id"),
            col("data.image_data").alias("image_data"),
            col("__meta__")
        )

        df_partitioned = df_flattened.withColumn(
            "data_type",
            when(
                col("__meta__.savedproject.processor").isNotNull(),
                lower(col("__meta__.savedproject.processor"))
            ).otherwise(lit("unknown"))
        ).drop("__meta__")

        # Apply Scala UDF to decrypt image fields
        df_with_decrypt = df_partitioned.withColumn(
            "decrypt_result",
            expr("decrypt_and_parse(image_view, image_id, image_data)")
        )

        df_with_fields = df_with_decrypt.select(
            col("projectguid"),
            col("project_type"),
            col("project_subtype"),
            col("userid"),
            col("inserted"),
            col("updated"),
            col("product_index"),
            col("product_type"),
            col("productguid"),
            col("productimageid"),
            col("decrypt_result.msp").alias("msp"),
            col("decrypt_result.mspid").alias("mspid"),
            col("decrypt_result.mediaid").alias("mediaid"),
            col("decrypt_result.locationspec").alias("locationspec"),
            col("data_type"),
            col("image_view"),
            col("image_id"),
            col("image_data")
        )

        # OPTIMIZATION: Cache df_with_fields since it's used for:
        # 1. Combined metrics + data_type aggregation
        # 2. Valid records filter (df_transformed)
        # 3. Dropped records filter (df_dropped)
        # This prevents re-executing the expensive UDF 3 times!
        if input_count >= cache_threshold:
            df_with_fields.cache()
            print(f"[TRANSFORM] Cached post-UDF DataFrame (records >= {cache_threshold})")

        decryption_failed_condition = (
            (col("msp").isNull()) &
            (col("mspid").isNull()) &
            (col("mediaid").isNull()) &
            (col("locationspec").isNull())
        )

        # OPTIMIZATION: Combined aggregation - metrics AND data_type distribution in ONE query
        # This replaces 2 separate scans with 1
        metrics_agg = df_with_fields.groupBy("data_type").agg(
            count("*").alias("total_count"),
            spark_sum(when(decryption_failed_condition, 1).otherwise(0)).alias("dropped_count")
        ).collect()

        # Process aggregation results
        total_count = 0
        dropped_count = 0
        data_type_stats = {}

        for row in metrics_agg:
            dt = row['data_type']
            dt_total = row['total_count'] or 0
            dt_dropped = row['dropped_count'] or 0
            dt_valid = dt_total - dt_dropped

            total_count += dt_total
            dropped_count += dt_dropped
            data_type_stats[dt] = {'records': dt_valid, 'dropped': dt_dropped}

        output_count = total_count - dropped_count

        print(f"[TRANSFORM] Completed transformation with {output_count} output records")
        if dropped_count > 0:
            print(f"[TRANSFORM] WARNING: {dropped_count} records failed decryption")
            print(f"[TRANSFORM]   Input: {input_count}, Output: {output_count}, Dropped: {dropped_count}")

        # Print data_type distribution
        print("[TRANSFORM] Data type distribution:")
        for dt, stats in sorted(data_type_stats.items()):
            print(f"[TRANSFORM]   - {dt}: {stats['records']} records, {stats['dropped']} dropped")

        if metrics:
            metrics.transform_records_output = output_count
            metrics.transform_data_types = data_type_stats
            if dropped_count > 0:
                metrics.transform_decryption_failures = dropped_count
                metrics.record_drop("transform_decryption_failure", dropped_count)

        # Validate totals
        if output_count + dropped_count != input_count:
            missing = input_count - (output_count + dropped_count)
            print(f"[TRANSFORM] WARNING: {missing} records unaccounted for (input: {input_count}, output: {output_count}, dropped: {dropped_count})")

        # Valid: at least one decrypted field is non-null (uses cached df_with_fields)
        df_transformed = df_with_fields.filter(
            (col("msp").isNotNull()) |
            (col("mspid").isNotNull()) |
            (col("mediaid").isNotNull()) |
            (col("locationspec").isNotNull())
        ).drop("image_view", "image_id", "image_data")

        # Dropped: all decrypted fields are null (uses cached df_with_fields)
        df_dropped = df_with_fields.filter(decryption_failed_condition).select(
            col("updated").alias("eventTime"),
            col("updated").alias("event_time"),
            struct(
                col("projectguid"),
                col("project_type"),
                col("project_subtype"),
                col("userid"),
                col("inserted"),
                col("updated"),
                col("product_index"),
                col("product_type"),
                col("productguid"),
                col("productimageid"),
                col("image_view"),
                col("image_id"),
                col("image_data"),
            ).alias("data"),
            spark_lit("transform_decryption_failure").alias("drop_reason"),
            spark_lit("transform").alias("drop_phase")
        )

        # Note: df_with_fields cache will be used by df_transformed and df_dropped
        # when they are materialized downstream (in loader)

        return df_transformed, df_dropped
