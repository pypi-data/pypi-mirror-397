from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
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


class TestParquetStrategy:
    """Unit tests for ParquetStrategy - focus on simple, isolated functionality"""
    
    def test_init_default_params(self):
        """Test constructor with default parameters"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = ParquetDataSourceStrategy(spark, schema_service, "s3a://bucket/path")
        
        assert strategy.spark == spark
        assert strategy.schema_service == schema_service
        assert strategy.base_path == "s3a://bucket/path"
        assert strategy.recursive is False
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from path"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = ParquetDataSourceStrategy(spark, schema_service, "s3a://bucket/path/")
        
        assert strategy.base_path == "s3a://bucket/path"
    
    def test_init_with_recursive_flag(self):
        """Test constructor with recursive flag"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = ParquetDataSourceStrategy(spark, schema_service, "s3a://bucket/path", recursive=True)
        
        assert strategy.recursive is True
    
    def test_get_type_returns_parquet(self):
        """Test that strategy type is PARQUET"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        strategy = ParquetDataSourceStrategy(spark, schema_service, "s3a://bucket/path")
        
        assert strategy.get_type() == "PARQUET"
