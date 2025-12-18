from abc import ABC, abstractmethod
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy
from dwh.services.schema.schema_service import SchemaService


class JDBCDataSinkStrategy(DataSinkStrategy, ABC):
    """Abstract JDBC data sink strategy for database operations"""
    
    def __init__(self, spark: SparkSession, schema_service: SchemaService, jdbc_url: str, properties: dict, debug_schemas: bool = False):
        self.spark = spark
        self.schema_service = schema_service
        self.jdbc_url = jdbc_url
        self.properties = properties
        self.debug_schemas = debug_schemas
    
    @abstractmethod
    def get_type(self) -> str:
        """Get the type identifier for this sink strategy"""
        pass
    
    def write_sink_df(self, df: DataFrame, schema_ref: str, sink_table: str, mode: str = "overwrite", **kwargs) -> None:
        """Write DataFrame to database sink - template method"""
        # Get required schema from DDL
        required_schema = self.schema_service.get_schema(schema_ref, sink_table)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} INPUT SCHEMA ===")
            df.printSchema()
            print(f"\n=== {self.__class__.__name__} EXPECTED SCHEMA ({schema_ref}/{sink_table}) ===")
            print(required_schema)
        
        # Validate DataFrame schema matches required schema
        self._validate_schema_match(df, required_schema)
        
        # Note: Table creation should be handled by infrastructure/deployment, not data sinks
        
        # Handle mode
        if mode == "overwrite":
            truncate_sql = f"TRUNCATE TABLE {sink_table};"
            self.execute_sql(truncate_sql)
        
        # Database-specific write implementation
        self._write_dataframe(df, sink_table)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} WRITE COMPLETE ===")
            print(f"Wrote {df.count()} rows to {sink_table}")
        else:
            print(f"{self.get_type()} SINK: Successfully wrote {df.count()} rows to {sink_table}")
    
    @abstractmethod
    def _write_dataframe(self, df: DataFrame, sink_table: str) -> None:
        """Database-specific DataFrame write implementation"""
        pass
    
    def _validate_schema_match(self, df: DataFrame, required_schema: StructType) -> None:
        """Validate DataFrame schema matches required schema"""
        actual_schema = df.schema
        
        if len(actual_schema.fields) != len(required_schema.fields):
            raise ValueError(
                f"{self.get_type()} SCHEMA MISMATCH: Expected {len(required_schema.fields)} fields, "
                f"got {len(actual_schema.fields)} fields"
            )
        
        for required_field in required_schema.fields:
            actual_field = None
            for field in actual_schema.fields:
                if field.name == required_field.name:
                    actual_field = field
                    break
            
            if actual_field is None:
                raise ValueError(
                    f"{self.get_type()} SCHEMA MISMATCH: Required field '{required_field.name}' not found in DataFrame"
                )
            
            if actual_field.dataType != required_field.dataType:
                raise ValueError(
                    f"{self.get_type()} SCHEMA MISMATCH: Field '{required_field.name}' type mismatch. "
                    f"Expected {required_field.dataType}, got {actual_field.dataType}"
                )

    def execute_sql(self, sql: str) -> None:
        """Execute SQL statement against the database"""
        try:
            # Convert properties dict to Java Properties object
            java_props = self.spark._jvm.java.util.Properties()
            for key, value in self.properties.items():
                java_props.setProperty(key, value)
            
            # Get JDBC connection
            connection = self.spark._jvm.java.sql.DriverManager.getConnection(
                self.jdbc_url, java_props
            )
            
            # Execute SQL
            statement = connection.createStatement()
            statement.execute(sql)
            
            # Clean up
            statement.close()
            connection.close()
            
            print("JDBC SQL: Successfully executed SQL statement")
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute SQL against database: {str(e)}") from e
