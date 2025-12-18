"""
Functional tests for DataSerializer Spark functionality only
"""
import pytest
from dwh.data.data_serializer import DataSerializer
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder


@pytest.mark.functional
class TestDataSerializerSparkOnly:
    """Test DataSerializer Spark functionality"""
    
    def test_to_parquet_with_builder(self, spark_session, schema_service, tmp_path):
        """Test Spark parquet output with builder"""
        builder = PromotionDataBuilder(schema_service)
        builder.add_record(name="Test Promotion", properties_promotionType="BOGO")
        
        output_path = tmp_path / "test_spark.parquet"
        
        result_path = DataSerializer.to_parquet(
            builder, 
            str(output_path), 
            spark_session
        )
        
        assert result_path == str(output_path)
        assert output_path.exists()
    
    def test_to_parquet_with_records(self, spark_session, schema_service, tmp_path):
        """Test Spark parquet output with raw records"""
        builder = PromotionDataBuilder(schema_service)
        records = builder.add_record(name="Test Promotion", properties_promotionType="BOGO").to_records()
        schema = builder.schema
        
        output_path = tmp_path / "test_records_spark.parquet"
        
        result_path = DataSerializer.to_parquet(
            records, 
            str(output_path), 
            spark_session, 
            schema
        )
        
        assert result_path == str(output_path)
        assert output_path.exists()
    
    def test_from_parquet(self, spark_session, schema_service, tmp_path):
        """Test reading parquet files"""
        builder = PromotionDataBuilder(schema_service)
        original_records = builder.add_record(name="Test Promotion", properties_promotionType="BOGO").to_records()
        
        output_path = tmp_path / "test_read.parquet"
        
        # Write parquet
        DataSerializer.to_parquet(
            original_records, 
            str(output_path), 
            spark_session, 
            builder.schema
        )
        
        # Read back
        read_records = DataSerializer.from_parquet(str(output_path), spark_session)
        
        assert len(read_records) == 1
        assert read_records[0]['name'] == "Test Promotion"
        assert read_records[0]['properties_promotionType'] == "BOGO"