from dwh.services.data_sink.redshift_data_sink_strategy import RedshiftDataSinkStrategy
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


class TestRedshiftDataSinkStrategy:
    """Unit tests for RedshiftDataSinkStrategy - focus on simple, isolated functionality"""
    
    def test_init_with_all_parameters(self):
        """Test constructor with all parameters"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        jdbc_url = "jdbc:redshift://cluster.region.redshift.amazonaws.com:5439/dev"
        s3_staging_path = "s3://bucket/staging/"
        properties = {"user": "testuser", "password": "testpass"}
        
        strategy = RedshiftDataSinkStrategy(spark, schema_service, jdbc_url, s3_staging_path, properties)
        
        assert strategy.spark == spark
        assert strategy.schema_service == schema_service
        assert strategy.jdbc_url == jdbc_url
        assert strategy.s3_staging_path == s3_staging_path
        assert strategy.properties == properties
    
    def test_init_with_empty_properties(self):
        """Test constructor with empty properties dict"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        jdbc_url = "jdbc:redshift://cluster.region.redshift.amazonaws.com:5439/dev"
        s3_staging_path = "s3://bucket/staging/"
        
        strategy = RedshiftDataSinkStrategy(spark, schema_service, jdbc_url, s3_staging_path, {})
        
        assert strategy.properties == {}
    
    def test_get_type_returns_redshift(self):
        """Test that strategy type is REDSHIFT"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = RedshiftDataSinkStrategy(spark, schema_service, "jdbc:redshift://test", "s3://test/", {})
        
        assert strategy.get_type() == "REDSHIFT"