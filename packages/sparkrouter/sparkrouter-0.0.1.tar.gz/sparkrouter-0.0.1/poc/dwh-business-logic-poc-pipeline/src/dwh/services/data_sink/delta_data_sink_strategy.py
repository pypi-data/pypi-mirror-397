from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy
from dwh.services.schema.schema_service import SchemaService


class DeltaDataSinkStrategy(DataSinkStrategy):
    """Strategy for Delta Lake operations"""

    def __init__(
            self,
            spark: SparkSession,
            schema_service: SchemaService,
            path: str,
            debug_schemas: bool = False
    ):
        self.spark = spark
        self.schema_service = schema_service
        self.base_path = path.rstrip('/')
        self.debug_schemas = debug_schemas

    def write_sink_df(self, df: DataFrame, schema_ref: str, sink_table: str, mode: str = "overwrite", **kwargs) -> None:
        # Get required schema from DDL
        required_schema = self.schema_service.get_schema(schema_ref, sink_table)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} INPUT SCHEMA ===")
            df.printSchema()
            print(f"\n=== {self.__class__.__name__} EXPECTED SCHEMA ({schema_ref}/{sink_table}) ===")
            print(required_schema)
        
        # Validate DataFrame schema matches required schema before writing
        self._validate_schema_match(df, required_schema)
        
        # Write using isolated backend operation - base_path is already the full path
        self._write_delta_file(df, self.base_path, mode)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} WRITE COMPLETE ===")
            print(f"Wrote {df.count()} rows to {self.base_path}")
        else:
            print(f"DELTA SINK: Successfully wrote {df.count()} rows to {self.base_path}")
    
    def _write_delta_file(self, df: DataFrame, full_path: str, mode: str) -> None:
        """Isolated backend operation for writing delta files"""
        df.write.format("delta").mode(mode).save(full_path)

    def _validate_schema_match(self, df: DataFrame, required_schema: StructType) -> None:
        """
        Validate DataFrame schema exactly matches required schema before writing.
        
        GUARDS AGAINST:
        - Writing data with wrong field names
        - Writing data with wrong types
        - Missing required fields
        - Extra unexpected fields
        
        ENFORCEMENT:
        - Exact field name and type matching
        - Fail fast on any deviation
        - Maintain data integrity
        """
        actual_schema = df.schema
        
        # Check field count matches
        if len(actual_schema.fields) != len(required_schema.fields):
            raise ValueError(
                f"SINK SCHEMA MISMATCH: Expected {len(required_schema.fields)} fields, "
                f"got {len(actual_schema.fields)} fields"
            )
        
        # Check each field matches exactly
        for required_field in required_schema.fields:
            actual_field = None
            for field in actual_schema.fields:
                if field.name == required_field.name:
                    actual_field = field
                    break
            
            if actual_field is None:
                raise ValueError(
                    f"SINK SCHEMA MISMATCH: Required field '{required_field.name}' not found in DataFrame"
                )
            
            if actual_field.dataType != required_field.dataType:
                raise ValueError(
                    f"SINK SCHEMA MISMATCH: Field '{required_field.name}' type mismatch. "
                    f"Expected {required_field.dataType}, got {actual_field.dataType}"
                )
        
        print("SINK SCHEMA VALIDATION PASSED: DataFrame schema matches required schema exactly")
    
    def get_type(self) -> str:
        return "DELTA"
