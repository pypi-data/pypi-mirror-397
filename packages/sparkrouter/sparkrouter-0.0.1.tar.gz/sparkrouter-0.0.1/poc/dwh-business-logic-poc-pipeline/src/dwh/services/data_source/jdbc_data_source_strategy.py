from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.services.database.table_registry import TableRegistry
from dwh.services.schema.schema_service import SchemaService


class JDBCDataSourceStrategy(DataSourceStrategy):
    """
    Strategy for accessing data via JDBC connections with strict schema enforcement.
    
    REQUIREMENTS:
    - Data quality and schema conformity is paramount
    - Zero tolerance for silent data corruption
    - Exact schema match required - no missing fields, extra fields, or type changes
    - Fail fast on any schema deviation
    
    JDBC BEHAVIOR LEARNINGS & GUARDS:
    
    1. JDBC SCHEMA INFERENCE:
       - JDBC provides actual database schema information
       - Can validate against database metadata before reading
       - GUARD: Compare database schema with required schema exactly
    
    2. TYPE MAPPING ISSUES:
       - JDBC to Spark type mapping can be inconsistent
       - Database types may not map exactly to expected Spark types
       - GUARD: Validate actual DataFrame schema after read
    
    3. TABLE NAMING:
       - Spark SQL cannot query 'schema.table' directly
       - Must register as temporary views with modified names
       - GUARD: Consistent naming convention for view registration
    
    IMPLEMENTATION STRATEGY:
    1. Read with required schema enforcement
    2. Validate JDBC type mapping didn't cause issues
    3. Register with proper naming conventions
    4. Fail explicitly on any deviation
    
    Table Registration:
    - 'schema.table' becomes 'schema_table' (dots replaced with underscores)
    - Also registers just the table part as convenience
    """

    def __init__(
            self,
            spark: SparkSession,
            schema_service: SchemaService,
            jdbc_url: str,
            properties: dict,
            debug_schemas: bool = False
    ):
        self.spark = spark
        self.schema_service = schema_service
        self.jdbc_url = jdbc_url
        self.properties = properties
        self.debug_schemas = debug_schemas

    def get_type(self):
        return "JDBC"

    def get_source_df(self, schema_ref: str, table_name: str) -> DataFrame:
        # Get required schema from DDL
        required_schema = self.schema_service.get_schema(schema_ref, table_name)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} EXPECTED SCHEMA ({schema_ref}/{table_name}) ===")
            print(required_schema)
            print("\nSpecific field expectations:")
            for field in required_schema.fields:
                if field.name in ['dailystarttime', 'dailyendtime', 'eventinstime', 'eventupdtime']:
                    print(f"  {field.name}: {field.dataType}")
        
        # Read data using backend-specific method
        df = self._read_jdbc_data(table_name, required_schema)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} OUTPUT SCHEMA ===")
            df.printSchema()
            print(f"Row count: {df.count()}")
        
        # CRITICAL: Validate database schema matches required schema exactly
        # Guards against database schema drift and type mapping issues
        self._validate_no_jdbc_type_issues(df, required_schema, table_name)
        
        # Register table with proper naming conventions
        self._register_table(df, table_name)
        
        return df
    
    def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
        """
        Pure backend I/O method for reading JDBC data.
        Contains only JDBC-specific read operations.
        """
        # CRITICAL: Read WITHOUT schema (JDBC doesn't support schema override)
        # JDBC determines schema from database metadata
        df = self.spark.read.jdbc(url=self.jdbc_url, table=table_name, properties=self.properties)
        
        # DEBUG: Show what JDBC actually returns before conversion
        print(f"\n=== JDBC RAW DATA FROM DATABASE ({table_name}) ===")
        print("Raw JDBC schema:")
        df.printSchema()
        if df.count() > 0:
            print("Raw JDBC data sample:")
            df.show(1, truncate=False)
            
            # Show specific problematic fields
            problematic_fields = ['eventinstime', 'eventupdtime', 'dwcreatedby', 'etl_created_by']
            for field_name in problematic_fields:
                if field_name in [f.name for f in df.schema.fields]:
                    field = next(f for f in df.schema.fields if f.name == field_name)
                    sample_values = df.select(field_name).collect()
                    if sample_values:
                        print(f"  {field_name}: {field.dataType} = {sample_values[0][field_name]} (Python type: {type(sample_values[0][field_name])})")
        
        # Apply JDBC type conversions to match DDL expectations
        converted_df = self.schema_service.convert_jdbc_to_ddl_types(df, required_schema)
        
        # DEBUG: Show what conversion produces
        print(f"\n=== AFTER JDBC CONVERSION ({table_name}) ===")
        print("Converted schema:")
        converted_df.printSchema()
        if converted_df.count() > 0:
            print("Converted data sample:")
            converted_df.show(1, truncate=False)
        
        return converted_df

    def _validate_no_jdbc_type_issues(self, df: DataFrame, required_schema: StructType, table_name: str) -> None:
        """
        Validate JDBC type mapping didn't cause schema issues.
        
        GUARDS AGAINST:
        - JDBC type mapping inconsistencies
        - Unexpected null values from database
        - Type conversion artifacts
        
        ENFORCEMENT:
        - Schema fields match exactly
        - No unexpected null patterns
        - Type consistency validation with JDBC mapping tolerance
        """
        # Validate schema matches exactly
        actual_fields = {f.name: f.dataType for f in df.schema.fields}
        required_fields = {f.name: f.dataType for f in required_schema.fields}
        
        # Check for missing fields
        missing_fields = set(required_fields.keys()) - set(actual_fields.keys())
        if missing_fields:
            raise ValueError(
                f"JDBC SCHEMA VIOLATION: Table '{table_name}' missing required fields {missing_fields}. "
                f"Database schema does not match DDL specification."
            )
        
        # Check for extra fields
        extra_fields = set(actual_fields.keys()) - set(required_fields.keys())
        if extra_fields:
            raise ValueError(
                f"JDBC SCHEMA VIOLATION: Table '{table_name}' has unexpected extra fields {extra_fields}. "
                f"Database schema does not match DDL specification."
            )
        
        # Check for type mismatches
        type_mismatches = []
        for field_name in required_fields:
            if actual_fields[field_name] != required_fields[field_name]:
                type_mismatches.append(
                    f"{field_name}: expected {required_fields[field_name]}, got {actual_fields[field_name]}"
                )
        
        if type_mismatches:
            raise ValueError(
                f"JDBC SCHEMA VIOLATION: Table '{table_name}' type mismatches prevent data integrity: {type_mismatches}. "
                f"JDBC type mapping does not match DDL specification."
            )
        
        # Check for suspicious null patterns (database data quality issues)
        total_rows = df.count()
        if total_rows > 0:
            for field in required_schema.fields:
                if not field.nullable:
                    null_count = df.filter(df[field.name].isNull()).count()
                    if null_count > 0:
                        raise ValueError(
                            f"JDBC DATA QUALITY VIOLATION: Non-nullable field '{field.name}' in table '{table_name}' "
                            f"has {null_count} null values. Database data does not meet schema requirements."
                        )
        
        print(f"JDBC SCHEMA VALIDATION PASSED: Table '{table_name}' schema and data integrity verified")

    def _register_table(self, df: DataFrame, table_name: str) -> None:
        """
        Register DataFrame with proper naming conventions for Spark SQL compatibility.
        
        NAMING STRATEGY:
        - 'schema.table' becomes 'schema_table' (dots to underscores)
        - Also registers table name alone for convenience
        """
        # Use TableRegistry with proper naming conventions
        TableRegistry.register_table(df, table_name)
        
        print(f"JDBC TABLE REGISTERED: '{table_name}' available for Spark SQL queries")
