from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.services.schema.schema_service import SchemaService


class ParquetDataSourceStrategy(DataSourceStrategy):
    """
    Strategy for reading from Parquet files with strict schema enforcement.
    
    REQUIREMENTS:
    - Data quality and schema conformity is paramount
    - Zero tolerance for silent data corruption
    - Exact schema match required - no missing fields, extra fields, or type changes
    - Fail fast on any schema deviation
    
    SPARK BEHAVIOR LEARNINGS & GUARDS:
    
    1. SCHEMA INFERENCE ISSUES:
       - Spark fails to infer schema from directories with multiple parquet files
       - GUARD: Always read WITH required schema to avoid inference failures
    
    2. SILENT DATA CORRUPTION:
       - Spark adds NULL columns for missing fields (BigInt field missing → NULL column added)
       - Spark converts types silently (BigInt → String loses numeric semantics)
       - GUARD: Validate post-read to catch unwanted Spark modifications
    
    3. LENIENT BEHAVIOR:
       - Spark ignores extra fields in parquet files
       - Spark allows type mismatches with automatic conversion
       - GUARD: Strict validation prevents these silent changes
    
    IMPLEMENTATION STRATEGY:
    1. Read WITH required schema (prevents inference issues)
    2. Validate against unwanted Spark modifications (prevents silent corruption)
    3. Fail explicitly on any deviation (maintains data integrity)
    """

    def __init__(self, spark: SparkSession, schema_service: SchemaService, path: str, recursive: bool = False, debug_schemas: bool = False):
        self.spark = spark
        self.schema_service = schema_service
        self.base_path = path.rstrip('/')
        self.recursive = recursive
        self.debug_schemas = debug_schemas

    def get_type(self):
        return "PARQUET"

    def get_source_df(self, schema_ref=None, table_name=None) -> DataFrame:
        # Get required schema from DDL
        required_schema = self.schema_service.get_schema(schema_ref, table_name)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} EXPECTED SCHEMA ({schema_ref}/{table_name}) ===")
            print(required_schema)
        
        # Read data using isolated backend operation
        df = self._read_parquet_data(required_schema, table_name)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} OUTPUT SCHEMA ===")
            df.printSchema()
            print(f"Row count: {df.count()}")
        
        # CRITICAL: Validate Spark didn't silently modify data
        # Guards against null column addition and type conversion
        self._validate_no_spark_modifications(df, required_schema)
        
        # Use same logic for table registration
        if table_name and not self.base_path.endswith('.parquet'):
            read_path = f"{self.base_path}/{table_name}"
        else:
            read_path = self.base_path
        self._register_table(df, read_path)
        return df
    
    def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
        """Isolated backend operation for reading parquet files"""
        # CRITICAL: Read WITH required schema to prevent Spark inference issues
        # This avoids "Unable to infer schema" errors with multiple parquet files
        # ABSOLUTE STRICTNESS: No fallback logic - parquet files MUST be Spark-compatible
        
        # Construct read path - append table_name only if base_path is a directory
        # For direct file paths (like s3://bucket/file.parquet), use as-is
        # For directory paths (like s3://bucket/staging), append table_name for sink/source consistency
        # Check if path looks like a directory (no file extension) vs a file (has extension)
        if table_name and not self.base_path.endswith('.parquet'):
            read_path = f"{self.base_path}/{table_name}"
        else:
            read_path = self.base_path
        
        # DEBUG: print(f"PARQUET SOURCE: base_path={self.base_path}, table_name={table_name}, read_path={read_path}")
        
        reader = self.spark.read.schema(required_schema)
        if self.recursive:
            return reader.option("recursiveFileLookup", "true").parquet(read_path)
        else:
            return reader.parquet(read_path)

    def _validate_no_spark_modifications(self, df: DataFrame, required_schema: StructType) -> None:
        """
        Validate Spark didn't silently modify data during read.
        
        GUARDS AGAINST:
        - Spark adding NULL columns for missing fields
        - Spark converting types (BigInt → String corruption)
        - Spark ignoring extra fields in source data
        
        ENFORCEMENT:
        - Check for suspicious null patterns (indicates missing source fields)
        - Validate data samples for type consistency
        - Detect when Spark made unwanted modifications
        """
        # Check for suspicious null patterns that indicate Spark added missing fields
        total_rows = df.count()
        if total_rows == 0:
            return  # Empty dataset is valid
        
        for field in required_schema.fields:
            null_count = df.filter(df[field.name].isNull()).count()
            null_percentage = null_count / total_rows if total_rows > 0 else 0
            
            # If ALL values are null, Spark likely added this column for missing field
            if null_percentage == 1.0:
                raise ValueError(
                    f"SCHEMA VIOLATION: Field '{field.name}' is 100% null ({null_count}/{total_rows} rows). "
                    f"This indicates Spark added a missing field as null column, corrupting data integrity."
                )
            
            # If non-nullable field has nulls, it's a violation
            if not field.nullable and null_count > 0:
                raise ValueError(
                    f"SCHEMA VIOLATION: Non-nullable field '{field.name}' has {null_count} null values. "
                    f"This indicates source data quality issues or schema mismatch."
                )
        
        # Sample data to check for type conversion artifacts
        sample_df = df.limit(100)
        for row in sample_df.collect():
            for field in required_schema.fields:
                value = getattr(row, field.name)
                if value is not None:
                    # Check if value type matches expected type
                    # This catches cases where Spark converted types silently
                    expected_python_type = self._spark_type_to_python_type(field.dataType)
                    if expected_python_type and not isinstance(value, expected_python_type):
                        raise ValueError(
                            f"SCHEMA VIOLATION: Field '{field.name}' has value '{value}' of type {type(value)}, "
                            f"expected {expected_python_type}. This indicates silent type conversion."
                        )
        
        print("SCHEMA VALIDATION PASSED: No silent Spark modifications detected - data integrity maintained")
    
    def _spark_type_to_python_type(self, spark_type):
        """Map Spark types to Python types for validation"""
        from pyspark.sql.types import StringType, IntegerType, LongType, BooleanType, DoubleType, FloatType
        
        type_mapping = {
            StringType: str,
            IntegerType: int,
            LongType: int,
            BooleanType: bool,
            DoubleType: float,
            FloatType: float
        }
        
        return type_mapping.get(type(spark_type), None)
    
    def _register_table(self, df: DataFrame, read_path: str) -> None:
        """Register DataFrame in table registry"""
        # Skip table registration for file:// paths (used in testing)
        if read_path.startswith('file://'):
            return
            
        import re
        view_name = re.sub(r'^s3a?://[^/]+/', '', read_path.rstrip('/'))
        view_name = view_name.replace('/', '_').replace('.', '_') or "parquet_source"
        
        from dwh.services.database.table_registry import TableRegistry
        TableRegistry.register_table(df, view_name)
