"""
Functional tests for ParquetDataBuilder
"""
import pytest
from dwh.data.parquet_data_builder import ParquetDataBuilder
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder


@pytest.mark.functional
class TestParquetDataBuilder:
    """Test ParquetDataBuilder functionality"""
    
    def test_to_parquet_spark_with_builder(self, spark_session, schema_service, tmp_path):
        """Test Spark parquet output with builder"""
        builder = PromotionDataBuilder(schema_service)
        builder.add_record(name="Test Promotion", properties_promotionType="BOGO")
        
        output_path = tmp_path / "test_spark.parquet"
        
        result_path = ParquetDataBuilder.to_parquet_spark(
            str(output_path), 
            builder, 
            spark_session
        )
        
        assert result_path == str(output_path)
        assert output_path.exists()
    
    def test_to_parquet_pyarrow_with_builder(self, schema_service, tmp_path):
        """Test PyArrow parquet output with builder"""
        builder = PromotionDataBuilder(schema_service)
        builder.add_record(name="Test Promotion", properties_promotionType="BOGO")
        
        output_path = tmp_path / "test_pyarrow.parquet"
        
        result_path = ParquetDataBuilder.to_parquet_pyarrow(
            str(output_path), 
            builder
        )
        
        assert result_path == str(output_path)
        assert output_path.exists()
    
    def test_to_parquet_spark_with_records(self, spark_session, schema_service, tmp_path):
        """Test Spark parquet output with raw records"""
        builder = PromotionDataBuilder(schema_service)
        records = builder.add_record(name="Test Promotion", properties_promotionType="BOGO").to_records()
        schema = builder.schema
        
        output_path = tmp_path / "test_records_spark.parquet"
        
        result_path = ParquetDataBuilder.to_parquet_spark(
            str(output_path), 
            records, 
            spark_session, 
            schema
        )
        
        assert result_path == str(output_path)
        assert output_path.exists()
    
    def test_to_parquet_pyarrow_with_records(self, schema_service, tmp_path):
        """Test PyArrow parquet output with raw records"""
        builder = PromotionDataBuilder(schema_service)
        records = builder.add_record(name="Test Promotion", properties_promotionType="BOGO").to_records()
        schema = builder.schema
        
        output_path = tmp_path / "test_records_pyarrow.parquet"
        
        result_path = ParquetDataBuilder.to_parquet_pyarrow(
            str(output_path), 
            records, 
            schema
        )
        
        assert result_path == str(output_path)
        assert output_path.exists()