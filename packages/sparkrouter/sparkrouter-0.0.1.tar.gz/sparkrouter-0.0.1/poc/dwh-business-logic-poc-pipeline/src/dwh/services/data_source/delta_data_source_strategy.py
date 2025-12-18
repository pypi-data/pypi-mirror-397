from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.services.schema.schema_service import SchemaService


class DeltaDataSourceStrategy(DataSourceStrategy):
    """
    Strategy for Delta Lake operations with strict schema enforcement.
    
    REQUIREMENTS:
    - Data quality and schema conformity is paramount
    - Zero tolerance for silent data corruption
    - Exact schema match required - no missing fields, extra fields, or type changes
    - Fail fast on any schema deviation
    
    DELTA BEHAVIOR LEARNINGS & GUARDS:
    
    1. DELTA SCHEMA EVOLUTION:
       - Delta Lake supports schema evolution by default
       - Can automatically add columns or change types
       - GUARD: Read with required schema to prevent unwanted evolution
    
    2. DELTA VERSIONING:
       - Delta Lake maintains transaction log and versioning
       - Schema can change between versions
       - GUARD: Validate schema matches expected at read time
    
    3. DELTA MERGE BEHAVIOR:
       - Delta merge operations can introduce schema changes
       - Missing columns get added as nulls automatically
       - GUARD: Strict validation prevents silent schema drift
    
    IMPLEMENTATION STRATEGY:
    1. Read WITH required schema (prevents schema evolution)
    2. Validate against unwanted Delta modifications (prevents silent drift)
    3. Register with proper naming conventions
    4. Fail explicitly on any deviation (maintains data integrity)
    """

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

    def get_type(self) -> str:
        return "DELTA"

    def get_source_df(self, schema_ref: str, table_name: str) -> DataFrame:
        # Get required schema from DDL
        required_schema = self.schema_service.get_schema(schema_ref, table_name)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} EXPECTED SCHEMA ({schema_ref}/{table_name}) ===")
            print(required_schema)
        
        # Read data using backend-specific method
        df = self._read_delta_data()
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} OUTPUT SCHEMA ===")
            df.printSchema()
            print(f"Row count: {df.count()}")
        
        # CRITICAL: Validate actual schema matches required schema
        # Guards against schema evolution and ensures data integrity
        self._validate_schema_match(df, required_schema)
        
        self._register_table(df, table_name)
        return df
    
    def _read_delta_data(self) -> DataFrame:
        """
        Pure backend I/O method for reading Delta data.
        Contains only Delta-specific read operations.
        """
        # CRITICAL: Delta Lake doesn't support user-specified schemas
        # Read without schema and validate after to ensure data integrity
        reader = self.spark.read.format("delta")
        return reader.load(self.base_path)
    
    def _validate_schema_match(self, df: DataFrame, required_schema: StructType) -> None:
        """
        Validate actual DataFrame schema exactly matches required schema.
        
        GUARDS AGAINST:
        - Missing required fields
        - Extra unexpected fields
        - Type mismatches
        - Schema evolution issues
        
        ENFORCEMENT:
        - Exact field name and type matching
        - Fail fast on any deviation
        - Maintain data integrity
        """
        actual_schema = df.schema
        
        # Check field count matches
        if len(actual_schema.fields) != len(required_schema.fields):
            raise ValueError(
                f"SCHEMA MISMATCH: Expected {len(required_schema.fields)} fields, "
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
                    f"SCHEMA MISMATCH: Required field '{required_field.name}' not found in actual schema"
                )
            
            if actual_field.dataType != required_field.dataType:
                raise ValueError(
                    f"SCHEMA MISMATCH: Field '{required_field.name}' type mismatch. "
                    f"Expected {required_field.dataType}, got {actual_field.dataType}"
                )
        
        print("SCHEMA VALIDATION PASSED: Delta table schema matches required schema exactly")

    def _register_table(self, df: DataFrame, table_name: str) -> None:
        """Register DataFrame in table registry"""
        from dwh.services.database.table_registry import TableRegistry
        TableRegistry.register_table(df, table_name)
        
        print(f"DELTA TABLE REGISTERED: '{table_name}' available for Spark SQL queries")
