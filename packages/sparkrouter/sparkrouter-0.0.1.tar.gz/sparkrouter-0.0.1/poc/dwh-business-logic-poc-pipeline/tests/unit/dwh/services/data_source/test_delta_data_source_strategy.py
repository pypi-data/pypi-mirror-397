from dwh.services.data_source.delta_data_source_strategy import DeltaDataSourceStrategy
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


class TestDeltaDataSourceStrategy:
    """Unit tests for DeltaDataSourceStrategy - focus on simple, isolated functionality"""
    
    def test_init_default_params(self):
        """Test constructor with default parameters"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSourceStrategy(spark, schema_service, "s3a://bucket/delta/path")
        
        assert strategy.spark == spark
        assert strategy.schema_service == schema_service
        assert strategy.base_path == "s3a://bucket/delta/path"
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from path"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSourceStrategy(spark, schema_service, "s3a://bucket/delta/path/")
        
        assert strategy.base_path == "s3a://bucket/delta/path"
    
    def test_get_type_returns_delta(self):
        """Test that strategy type is DELTA"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSourceStrategy(spark, schema_service, "s3a://bucket/delta/path")
        
        assert strategy.get_type() == "DELTA"
