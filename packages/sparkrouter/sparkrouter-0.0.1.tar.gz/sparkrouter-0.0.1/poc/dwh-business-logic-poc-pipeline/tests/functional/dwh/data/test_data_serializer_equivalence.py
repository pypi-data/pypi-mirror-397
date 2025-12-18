"""
Test to verify equivalence between Spark DataSerializer and PyArrow DataSerializer
"""
import pytest
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any

from dwh.data.data_serializer import DataSerializer
from dwh.data.pyarrow_data_serializer import PyArrowDataSerializer
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder


@pytest.mark.functional
class TestDataSerializerEquivalence:
    """Test equivalence between Spark and PyArrow data serializers"""
    
    @pytest.fixture
    def promotion_records(self, schema_service):
        """Create test promotion records using builder"""
        builder = PromotionDataBuilder(schema_service)
        
        # Create diverse test data to exercise different data types
        records = (builder
                  .add_records(2, 
                              name="Base Promotion",
                              properties_promotionType="PERCENTAGE_DISCOUNT")
                  .with_id("PROMO_COMPLEX_001")
                  .with_name("Complex Promotion")
                  .with_promotion_type("FIXED_DISCOUNT")
                  .with_tags("BLACK_FRIDAY", "ELECTRONICS", "SEASONAL")
                  .with_coupon_limits(5, 50)
                  .to_records())
        
        return records
    
    def test_parquet_equivalence(self, spark_session, schema_service, promotion_records, tmp_path):
        """Test that Spark and PyArrow produce equivalent parquet files"""
        schema = schema_service.get_schema(
            PromotionDataBuilder(schema_service).schema_ref,
            PromotionDataBuilder(schema_service).table_name
        )
        
        # Create output paths
        spark_output = tmp_path / "spark_output.parquet"
        pyarrow_output = tmp_path / "pyarrow_output.parquet"
        
        # Write using both serializers
        DataSerializer.to_parquet(promotion_records, str(spark_output), spark_session, schema)
        PyArrowDataSerializer.to_parquet(promotion_records, str(pyarrow_output), schema)
        
        # Verify both files exist
        assert spark_output.exists()
        assert pyarrow_output.exists()
        
        # Read back using both methods
        spark_read_records = DataSerializer.from_parquet(str(spark_output), spark_session)
        pyarrow_read_records = PyArrowDataSerializer.from_parquet(str(pyarrow_output))
        
        # Verify record counts match
        assert len(spark_read_records) == len(pyarrow_read_records)
        assert len(spark_read_records) == len(promotion_records)
        
        # Sort records by ID for consistent comparison
        spark_sorted = sorted(spark_read_records, key=lambda x: x['_id'])
        pyarrow_sorted = sorted(pyarrow_read_records, key=lambda x: x['_id'])
        
        # Compare each record
        for i, (spark_record, pyarrow_record) in enumerate(zip(spark_sorted, pyarrow_sorted)):
            self._assert_records_equivalent(spark_record, pyarrow_record, f"Record {i}")
    
    def test_empty_data_equivalence(self, spark_session, schema_service, tmp_path):
        """Test that both serializers handle empty data equivalently"""
        schema = schema_service.get_schema(
            PromotionDataBuilder(schema_service).schema_ref,
            PromotionDataBuilder(schema_service).table_name
        )
        
        empty_records = []
        
        # Create output paths
        spark_output = tmp_path / "spark_empty.parquet"
        pyarrow_output = tmp_path / "pyarrow_empty.parquet"
        
        # Write using both serializers
        DataSerializer.to_parquet(empty_records, str(spark_output), spark_session, schema)
        PyArrowDataSerializer.to_parquet(empty_records, str(pyarrow_output), schema)
        
        # Verify both files exist
        assert spark_output.exists()
        assert pyarrow_output.exists()
        
        # Read back using both methods
        spark_read_records = DataSerializer.from_parquet(str(spark_output), spark_session)
        pyarrow_read_records = PyArrowDataSerializer.from_parquet(str(pyarrow_output))
        
        # Verify both return empty lists
        assert len(spark_read_records) == 0
        assert len(pyarrow_read_records) == 0
    
    def test_builder_input_equivalence(self, spark_session, schema_service, tmp_path):
        """Test that both serializers handle builder input equivalently"""
        builder = PromotionDataBuilder(schema_service)
        builder.add_record(name="Builder Test", properties_promotionType="BOGO")
        
        # Create output paths
        spark_output = tmp_path / "spark_builder.parquet"
        pyarrow_output = tmp_path / "pyarrow_builder.parquet"
        
        # Write using both serializers with builder input
        DataSerializer.to_parquet(builder, str(spark_output), spark_session)
        PyArrowDataSerializer.to_parquet(builder, str(pyarrow_output))
        
        # Read back and compare
        spark_read_records = DataSerializer.from_parquet(str(spark_output), spark_session)
        pyarrow_read_records = PyArrowDataSerializer.from_parquet(str(pyarrow_output))
        
        assert len(spark_read_records) == 1
        assert len(pyarrow_read_records) == 1
        
        self._assert_records_equivalent(
            spark_read_records[0], 
            pyarrow_read_records[0], 
            "Builder record"
        )
    
    def test_complex_nested_structures(self, spark_session, schema_service, tmp_path):
        """Test equivalence with complex nested structures"""
        from dwh.data.dl_base.promotion.promotion_data_builder import DiscountTiersBuilder, BundleBuilder
        
        builder = PromotionDataBuilder(schema_service)
        
        # Create complex nested structures
        discount_tiers = (DiscountTiersBuilder()
                         .with_tiered_skus("ELECTRONICS_TV", "ELECTRONICS_LAPTOP")
                         .with_excluded_skus("CLEARANCE_ITEMS"))
        
        bundle_a = (BundleBuilder("COMPLEX_BUNDLE")
                   .with_promotion_skus("SKU_001", "SKU_002")
                   .with_excluded_skus("EXCLUDED_001")
                   .with_limits(2, 10))
        
        records = (builder
                  .with_id("PROMO_NESTED_001")
                  .with_name("Complex Nested Promotion")
                  .with_discount_tiers(discount_tiers)
                  .with_bundle("bundles_bundleA", bundle_a)
                  .to_records())
        
        schema = builder.schema
        
        # Create output paths
        spark_output = tmp_path / "spark_nested.parquet"
        pyarrow_output = tmp_path / "pyarrow_nested.parquet"
        
        # Write using both serializers
        DataSerializer.to_parquet(records, str(spark_output), spark_session, schema)
        PyArrowDataSerializer.to_parquet(records, str(pyarrow_output), schema)
        
        # Read back and compare
        spark_read_records = DataSerializer.from_parquet(str(spark_output), spark_session)
        pyarrow_read_records = PyArrowDataSerializer.from_parquet(str(pyarrow_output))
        
        assert len(spark_read_records) == 1
        assert len(pyarrow_read_records) == 1
        
        self._assert_records_equivalent(
            spark_read_records[0], 
            pyarrow_read_records[0], 
            "Complex nested record"
        )
    
    def _assert_records_equivalent(self, spark_record: Dict[str, Any], pyarrow_record: Dict[str, Any], context: str):
        """Assert that two records are equivalent, handling type differences"""
        assert set(spark_record.keys()) == set(pyarrow_record.keys()), f"{context}: Field sets differ"
        
        for field_name in spark_record.keys():
            spark_value = spark_record[field_name]
            pyarrow_value = pyarrow_record[field_name]
            
            self._assert_values_equivalent(
                spark_value, 
                pyarrow_value, 
                f"{context}.{field_name}"
            )
    
    def _assert_values_equivalent(self, spark_value: Any, pyarrow_value: Any, context: str):
        """Assert that two values are equivalent, handling type differences"""
        # Handle None values
        if spark_value is None and pyarrow_value is None:
            return
        
        # Handle datetime objects
        if hasattr(spark_value, 'timestamp') and hasattr(pyarrow_value, 'timestamp'):
            # Both are datetime-like, compare timestamps
            assert spark_value.timestamp() == pyarrow_value.timestamp(), f"{context}: Datetime values differ"
            return
        
        # Handle Spark Row vs PyArrow dict
        from pyspark.sql import Row
        if isinstance(spark_value, Row) and isinstance(pyarrow_value, dict):
            # Convert Spark Row to dict for comparison
            spark_dict = spark_value.asDict()
            assert set(spark_dict.keys()) == set(pyarrow_value.keys()), f"{context}: Row/Dict keys differ"
            for key in spark_dict.keys():
                self._assert_values_equivalent(
                    spark_dict[key], 
                    pyarrow_value[key], 
                    f"{context}.{key}"
                )
            return
        
        # Handle lists
        if isinstance(spark_value, list) and isinstance(pyarrow_value, list):
            assert len(spark_value) == len(pyarrow_value), f"{context}: List lengths differ"
            for i, (s_item, p_item) in enumerate(zip(spark_value, pyarrow_value)):
                self._assert_values_equivalent(s_item, p_item, f"{context}[{i}]")
            return
        
        # Handle dictionaries
        if isinstance(spark_value, dict) and isinstance(pyarrow_value, dict):
            assert set(spark_value.keys()) == set(pyarrow_value.keys()), f"{context}: Dict keys differ"
            for key in spark_value.keys():
                self._assert_values_equivalent(
                    spark_value[key], 
                    pyarrow_value[key], 
                    f"{context}.{key}"
                )
            return
        
        # Handle primitive types
        assert spark_value == pyarrow_value, f"{context}: Values differ - Spark: {spark_value}, PyArrow: {pyarrow_value}"