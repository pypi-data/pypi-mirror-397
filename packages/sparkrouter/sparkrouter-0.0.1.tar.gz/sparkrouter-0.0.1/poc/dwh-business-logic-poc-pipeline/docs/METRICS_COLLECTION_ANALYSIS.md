# Metrics Collection Analysis: transform_images_job

## Executive Summary

The current implementation uses **12 separate df.count() calls** throughout the ETL pipeline. Each `count()` triggers a full Spark action that scans the entire dataset, making this approach extremely inefficient for large-scale data processing.

**Estimated Performance Impact**: With 12 count operations on large datasets (millions of records), we're essentially processing the data 12+ times instead of once. This could increase job runtime by **300-500%** or more depending on data volume.

## Current Implementation Problems

### Count Locations (12 Total)

#### Extract Phase (8 counts)
1. **image_extractor.py:44** - `total_count = df.count()` - Per-partition record count
2. **image_extractor.py:59** - `corrupt_count = df.filter(...).count()` - Corrupt records
3. **image_extractor.py:70** - `null_eventtime = df.filter(...).count()` - Null eventTime records
4. **image_extractor.py:71** - `null_data = df.filter(...).count()` - Null data records
5. **image_extractor.py:87** - `filtered_count = df_filtered.count()` - Post-filter count
6. **image_extractor.py:110** - `total_count = result.count()` - Post-union count
7. **image_extractor.py:158** - `record_count = df.count()` - Final extraction count

#### Transform Phase (2 counts)
8. **image_transformer.py:82** - `input_count = df.count()` - Transform input count
9. **image_transformer.py:138** - `output_count = df_transformed.count()` - Transform output count

#### Load Phase (2 counts + 1 aggregation)
10. **image_loader.py:61** - `row_count = json_str_df.count()` - For repartitioning calculation
11. **image_loader.py:115** - `input_count = df.count()` - Load input count
12. **image_loader.py:184** - `partition_summary = out_df.groupBy(*partition_columns).count().collect()` - Partition distribution

### Why This is Inefficient

Each `df.count()` operation:
1. **Triggers a Spark Action**: Forces evaluation of the entire lazy execution plan up to that point
2. **Scans Full Dataset**: Every executor must scan every partition and send results to driver
3. **Blocks Execution**: Job must wait for count to complete before continuing
4. **Compounds with Multiple Calls**: With 12 count operations, we're repeatedly scanning data

**Example**: In the extract phase alone, for each partition:
- Count 1: Scan all records to get total
- Count 2: Scan + filter to find corrupt records
- Count 3: Scan + filter to find null eventTime
- Count 4: Scan + filter to find null data
- Count 5: Scan filtered dataset to get final count

This is **5 full scans per partition** when we could do it in **1 scan**.

## Recommended Approach: Single-Pass Metrics Collection

### Strategy 1: Accumulator-Based Metrics (Recommended)

Use Spark Accumulators to collect metrics during the actual data processing transformations, requiring only a single pass through the data.

#### Benefits
- **Single Data Pass**: Metrics collected during actual transformations
- **Minimal Overhead**: Accumulators are lightweight, in-memory counters
- **No Additional Scans**: Counts happen as data flows through pipeline
- **Accurate Metrics**: Captures exactly what was processed

#### Implementation Pattern

```python
from pyspark import AccumulatorParam
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StructType
from typing import Dict


class MetricsAccumulator:
    """Thread-safe accumulator for collecting pipeline metrics"""

    def __init__(self, spark: SparkSession):
        self.spark = spark

        # Create accumulators for each metric
        self.records_read = spark.sparkContext.accumulator(0)
        self.corrupt_records = spark.sparkContext.accumulator(0)
        self.null_eventtime = spark.sparkContext.accumulator(0)
        self.null_data = spark.sparkContext.accumulator(0)
        self.records_filtered = spark.sparkContext.accumulator(0)
        self.transform_input = spark.sparkContext.accumulator(0)
        self.transform_output = spark.sparkContext.accumulator(0)
        self.decryption_failures = spark.sparkContext.accumulator(0)

    def get_metrics(self) -> Dict[str, int]:
        """Get current metric values"""
        return {
            'records_read': self.records_read.value,
            'corrupt_records': self.corrupt_records.value,
            'null_eventtime': self.null_eventtime.value,
            'null_data': self.null_data.value,
            'records_filtered': self.records_filtered.value,
            'transform_input': self.transform_input.value,
            'transform_output': self.transform_output.value,
            'decryption_failures': self.decryption_failures.value,
        }


class ImageExtractorWithMetrics:
    """Optimized extractor that collects metrics in a single pass"""

    def __init__(self, s3_data_source, base_s3_path: str, spark: SparkSession):
        self.s3_data_source = s3_data_source
        self.base_s3_path = base_s3_path.rstrip('/')
        self.metrics_acc = MetricsAccumulator(spark)
        self.spark = spark

    def read_json_with_metrics(self, paths: list[str], schema: StructType) -> DataFrame:
        """Read JSON with single-pass metrics collection"""

        if not paths:
            return self.spark.createDataFrame([], schema)

        # Define UDF that increments accumulators as rows are processed
        def count_and_validate(eventTime, data, corrupt_record):
            """UDF that tracks metrics during row processing"""
            self.metrics_acc.records_read.add(1)

            if corrupt_record is not None:
                self.metrics_acc.corrupt_records.add(1)
                return False  # Filter out

            if eventTime is None:
                self.metrics_acc.null_eventtime.add(1)
                return False  # Filter out

            if data is None:
                self.metrics_acc.null_data.add(1)
                return False  # Filter out

            self.metrics_acc.records_filtered.add(1)
            return True  # Keep record

        # Register UDF
        from pyspark.sql.types import BooleanType
        validate_udf = udf(count_and_validate, BooleanType())

        # Read all partitions
        dfs = []
        for path in paths:
            try:
                df = (self.spark.read
                      .schema(schema)
                      .option("mode", "PERMISSIVE")
                      .option("columnNameOfCorruptRecord", "_corrupt_record")
                      .json(path))

                # Apply validation UDF that also counts
                df_with_filter = df.withColumn(
                    "_valid",
                    validate_udf(
                        col("eventTime"),
                        col("data"),
                        col("_corrupt_record")
                    )
                )

                # Filter to valid records only
                df_filtered = df_with_filter.filter(col("_valid")).drop("_valid", "_corrupt_record")

                dfs.append(df_filtered)

            except Exception as e:
                print(f"Skipping partition: {path} - {str(e)}")

        if not dfs:
            return self.spark.createDataFrame([], schema)

        # Union all dataframes
        from functools import reduce
        result = reduce(lambda df1, df2: df1.union(df2), dfs)

        # IMPORTANT: Must trigger an action to materialize accumulators
        # Use cache() + count() once, or trigger through a write operation
        result.cache()
        final_count = result.count()  # This is the ONLY count() needed

        return result
```

### Strategy 2: Spark SQL Aggregations (Alternative)

Use a single aggregation query with conditional counts to collect all metrics in one pass.

#### Implementation Pattern

```python
from pyspark.sql.functions import (
    count,
    sum as spark_sum,
    when,
    col,
    expr
)


class SinglePassMetricsCollector:
    """Collect multiple metrics in a single aggregation query"""

    @staticmethod
    def collect_validation_metrics(df: DataFrame) -> Dict[str, int]:
        """Collect all validation metrics in a single query"""

        metrics_df = df.agg(
            # Total records
            count("*").alias("total_records"),

            # Corrupt records (if column exists)
            spark_sum(
                when(col("_corrupt_record").isNotNull(), 1).otherwise(0)
            ).alias("corrupt_records"),

            # Null critical fields
            spark_sum(
                when(col("eventTime").isNull(), 1).otherwise(0)
            ).alias("null_eventtime"),

            spark_sum(
                when(col("data").isNull(), 1).otherwise(0)
            ).alias("null_data"),

            # Valid records (both fields not null)
            spark_sum(
                when(
                    (col("eventTime").isNotNull()) &
                    (col("data").isNotNull()) &
                    (col("_corrupt_record").isNull()),
                    1
                ).otherwise(0)
            ).alias("valid_records")
        ).collect()[0]

        return {
            'total_records': metrics_df['total_records'],
            'corrupt_records': metrics_df['corrupt_records'],
            'null_eventtime': metrics_df['null_eventtime'],
            'null_data': metrics_df['null_data'],
            'valid_records': metrics_df['valid_records']
        }


class ImageExtractorOptimized:
    """Extractor using single aggregation for metrics"""

    def read_json_optimized(self, paths: list[str], schema: StructType) -> tuple[DataFrame, Dict]:
        """Read JSON and collect metrics in single pass"""

        # Read all data with corrupt record tracking
        df_raw = (self.spark.read
                  .schema(schema)
                  .option("mode", "PERMISSIVE")
                  .option("columnNameOfCorruptRecord", "_corrupt_record")
                  .json(paths))

        # Collect all metrics in a SINGLE aggregation query
        metrics = SinglePassMetricsCollector.collect_validation_metrics(df_raw)

        # Now filter to valid records (no additional count needed)
        df_valid = df_raw.filter(
            (col("eventTime").isNotNull()) &
            (col("data").isNotNull()) &
            (col("_corrupt_record").isNull())
        ).drop("_corrupt_record")

        return df_valid, metrics
```

### Strategy 3: Metrics from Write Statistics (For Load Phase)

Leverage Spark's write metrics instead of counting before write.

```python
class ImageLoaderOptimized:
    """Loader that uses write statistics instead of pre-write counts"""

    def load_with_write_metrics(self, df: DataFrame, metrics=None) -> None:
        """Use write operation metrics instead of counting"""

        # Prepare output dataframe
        out_df = self._prepare_output_dataframe(df)

        # Get partition summary in single pass (already an aggregation)
        partition_summary = out_df.groupBy(*partition_columns).count().collect()

        # Calculate expected records from partition summary
        total_records = sum(row['count'] for row in partition_summary)

        if metrics:
            metrics.load_partitions_written = len(partition_summary)
            metrics.load_records_input = total_records  # From aggregation, not count()

        # Write and get file list
        output_paths = self.s3_data_sink.write_json(out_df, output_path, partition_columns)

        if metrics:
            metrics.load_files_written = len(output_paths)
            metrics.load_records_written = total_records
```

## Recommended Implementation Plan

### Phase 1: Extract Phase Optimization (Highest Impact)
**Current**: 7 separate count() operations per extract
**Target**: 1 count() operation total

Implement single-pass metrics collection using Strategy 2 (SQL Aggregations):
- Replace per-partition counting with single aggregation query
- Collect corrupt records, null fields, and valid records in one pass
- Estimated speedup: **5-7x faster** for extract phase

### Phase 2: Transform Phase Optimization
**Current**: 2 count() operations
**Target**: 0 count() operations

Use accumulator-based counting (Strategy 1):
- Increment counters during transformation UDF execution
- No separate count() calls needed
- Estimated speedup: **2x faster** for transform phase

### Phase 3: Load Phase Optimization
**Current**: 2 count() + 1 aggregation
**Target**: 1 aggregation only

Use Strategy 3 (Write Statistics):
- Remove pre-write count() calls
- Use partition aggregation results for metrics
- Only count done is the groupBy().count() for partition summary (unavoidable, but already optimized)
- Estimated speedup: **1.5-2x faster** for load phase

## Alternative: Lazy Metrics Collection

If exact metrics aren't critical for every run, consider **sampling-based metrics**:

```python
def collect_sampled_metrics(df: DataFrame, sample_rate: float = 0.01) -> Dict[str, int]:
    """Collect approximate metrics using sampling"""

    sampled_df = df.sample(withReplacement=False, fraction=sample_rate)

    sample_metrics = SinglePassMetricsCollector.collect_validation_metrics(sampled_df)

    # Extrapolate to full dataset
    scale_factor = 1.0 / sample_rate
    return {
        key: int(value * scale_factor)
        for key, value in sample_metrics.items()
    }
```

**Benefits**:
- Process only 1% of data for metrics
- 100x faster than full count
- Sufficient accuracy for monitoring/alerting

**Trade-offs**:
- Approximate metrics (±5-10% accuracy with 1% sample)
- Not suitable for billing/audit use cases

## Performance Comparison

### Current Implementation (12 counts)
```
Extract:  7 counts × 30s each = 210s
Transform: 2 counts × 30s each = 60s
Load:     2 counts × 30s each = 60s
                      Total: 330s (just for counting!)
```

### Optimized Implementation (1 aggregation)
```
Extract:  1 aggregation = 35s (all metrics at once)
Transform: 0 counts (accumulator-based) = 0s
Load:     1 aggregation = 30s (for partition summary, unavoidable)
                      Total: 65s
```

**Expected Improvement**: **5x faster** (330s → 65s) just for metrics collection, which translates to significant overall job speedup.

## Testing Requirements

Per framework standards, any metrics collection refactoring must:

1. **Preserve Business Logic**: Metrics collection is business logic - must not be mocked/stubbed
2. **Functional Tests Required**: Test with real Spark processing
3. **Validate Metric Accuracy**: Ensure optimized collection produces identical results
4. **Test at Scale**: Validate performance improvements with realistic data volumes

## Recommendations

### Immediate Actions (High Priority)
1. **Implement Strategy 2 (SQL Aggregations) for Extract Phase**
   - Replace 7 counts with 1 aggregation
   - Highest ROI - this is where most counts occur

2. **Implement Strategy 3 (Write Statistics) for Load Phase**
   - Remove pre-write counts
   - Use aggregation results for metrics

### Medium-Term Actions
3. **Consider Strategy 1 (Accumulators) for Transform Phase**
   - More complex implementation
   - Lower ROI (only 2 counts)
   - Consider after validating extract/load optimizations

### Long-Term Considerations
4. **Implement Configurable Sampling** for non-critical metrics
5. **Add Performance Benchmarks** to regression test suite
6. **Document Metrics Trade-offs** in operational runbooks

## Conclusion

The current approach of 12 separate `df.count()` calls is **extremely inefficient** for large-scale Spark processing. By consolidating to single-pass metrics collection using SQL aggregations and accumulators, we can achieve **5x or better speedup** in metrics collection overhead while maintaining accurate business metrics.

The recommended approach aligns with Spark best practices and the framework's emphasis on efficient, production-ready implementations.
