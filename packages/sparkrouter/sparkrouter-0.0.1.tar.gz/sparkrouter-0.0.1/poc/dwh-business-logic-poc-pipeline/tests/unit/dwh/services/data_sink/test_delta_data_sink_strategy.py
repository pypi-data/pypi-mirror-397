from pyspark.sql.types import StructType, StringType, StructField

from dwh.services.data_sink.delta_data_sink_strategy import DeltaDataSinkStrategy
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


class TestDeltaDataSinkStrategy:
    """Unit tests for DeltaDataSinkStrategy - focus on simple, isolated functionality"""
    
    def test_init_default_params(self):
        """Test constructor with default parameters"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSinkStrategy(spark, schema_service, "s3a://bucket/delta/path")
        
        assert strategy.spark == spark
        assert strategy.schema_service == schema_service
        assert strategy.base_path == "s3a://bucket/delta/path"
        assert strategy.debug_schemas is False
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from path"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSinkStrategy(spark, schema_service, "s3a://bucket/delta/path/")
        
        assert strategy.base_path == "s3a://bucket/delta/path"
    
    def test_init_with_debug_schemas_flag(self):
        """Test constructor with debug_schemas flag"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSinkStrategy(spark, schema_service, "s3a://bucket/delta/path", debug_schemas=True)
        
        assert strategy.debug_schemas is True
    
    def test_get_type_returns_delta(self):
        """Test that strategy type is DELTA"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = DeltaDataSinkStrategy(spark, schema_service, "s3a://bucket/delta/path")
        
        assert strategy.get_type() == "DELTA"
