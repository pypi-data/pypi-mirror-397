from pyspark.sql import DataFrame
from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy


class JsonLinesDataSinkStrategy(DataSinkStrategy):
    """Data sink strategy for writing Parquet files to S3"""

    def __init__(self, spark, schema_service, path: str, debug_schemas: bool = False):
        self.spark = spark
        self.schema_service = schema_service
        self.path = path
        self.debug_schemas = debug_schemas

    def write_sink_df(self, df: DataFrame, schema_ref: str, table_name: str, mode: str = "overwrite") -> None:
        """Write DataFrame as JSON Lines files to S3 path"""
        # Validate against sink schema
        sink_schema = self.schema_service.get_schema(schema_ref, table_name)
        validated_df = self._validate_and_apply_schema(df, sink_schema, f"{schema_ref}.{table_name}")

        # Write to S3 as Parquet
        full_path = f"{self.path}/{table_name}"
        # DEBUG: print(f"JSONL SINK: path={self.path}, table_name={table_name}, full_path={full_path}")
        self._write_json_lines_file(validated_df, full_path, mode)

    def _validate_and_apply_schema(self, df: DataFrame, required_schema, table_ref: str) -> DataFrame:
        """Validate DataFrame matches required schema"""
        if self.debug_schemas:
            print("\n=== PARQUET SINK INPUT SCHEMA ===")
            df.printSchema()
            print(f"\n=== PARQUET SINK EXPECTED SCHEMA ({table_ref}) ===")
            print(required_schema)

        # Apply the required schema to ensure compatibility
        try:
            validated_df = self.spark.createDataFrame(df.rdd, required_schema)
            if self.debug_schemas:
                print("\n=== PARQUET SINK SCHEMA VALIDATION PASSED ===")
            return validated_df
        except Exception as e:
            raise ValueError(f"PARQUET SINK SCHEMA VALIDATION FAILED for {table_ref}: {str(e)}")

    def _write_json_lines_file(self, df: DataFrame, full_path: str, mode: str) -> None:
        """Write DataFrame to JSONL file"""
        try:
            #  TODO: Write as JSON Lines
            df.write.mode(mode).json(full_path)
            print(f"JSONL SINK: Successfully wrote {df.count()} rows to {full_path}")
        except Exception as e:
            raise RuntimeError(f"JSONL SINK: Failed to write to {full_path}: {str(e)}")

    def get_type(self) -> str:
        return "PARQUET"
