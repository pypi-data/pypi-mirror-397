from dwh.services.data_source.jdbc_data_source_strategy import JDBCDataSourceStrategy
from pyspark.sql.types import StructType, StringType, StructField
from dwh.services.schema.schema_service import SchemaService
from unit.noops import NoopSparkSession


class NoopSchemaService(SchemaService):
    """Noop schema service for testing"""

    def get_schema(self, schema_ref: str, table_name: str) -> StructType:
        """Return a basic test schema"""
        fields = [
            StructField("_id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("updatedate", StringType(), True),
            StructField("ptn_ingress_date", StringType(), True)
        ]

        print(f"NOOP Schema: Retrieved schema for {table_name} from {schema_ref}")
        return StructType(fields)


class TestJDBCStrategy:
    """Unit tests for JDBCStrategy - focus on simple, isolated functionality"""
    
    def test_init_with_properties(self):
        """Test constructor with JDBC properties"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        jdbc_url = "jdbc:postgresql://localhost:5432/testdb"
        properties = {"user": "testuser", "password": "testpass"}
        
        strategy = JDBCDataSourceStrategy(spark, schema_service, jdbc_url, properties)
        
        assert strategy.spark == spark
        assert strategy.schema_service == schema_service
        assert strategy.jdbc_url == jdbc_url
        assert strategy.properties == properties
    
    def test_init_with_empty_properties(self):
        """Test constructor with empty properties dict"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        jdbc_url = "jdbc:postgresql://localhost:5432/testdb"
        
        strategy = JDBCDataSourceStrategy(spark, schema_service, jdbc_url, {})
        
        assert strategy.properties == {}
    
    def test_get_type_returns_jdbc(self):
        """Test that strategy type is JDBC"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = JDBCDataSourceStrategy(spark, schema_service, "jdbc:postgresql://localhost:5432/testdb", {})
        
        assert strategy.get_type() == "JDBC"
