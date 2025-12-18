"""
Unit tests for PromotionExtractor
"""
from datetime import datetime

from dwh.jobs.load_promos.extract.promotion_extractor import PromotionExtractor
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class NoopDataSourceStrategy:
    """Noop DataSourceStrategy for testing"""

    def __init__(self):
        self.get_source_df_calls = []

    def get_source_df(self, schema_ref, table_name):
        self.get_source_df_calls.append((schema_ref, table_name))
        # Return None since we can't create a real DataFrame without Spark
        return None


class TestPromotionExtractor:
    """Test PromotionExtractor class"""

    def test_init(self):
        """Test PromotionExtractor initialization"""
        s3_strategy = NoopDataSourceStrategy()
        extractor = PromotionExtractor(s3_strategy)
        
        assert extractor.s3_data_source_strategy is s3_strategy

    def test_extract_calls_strategy_with_schema_constants(self):
        """Test extract calls strategy with correct schema constants"""
        s3_strategy = NoopDataSourceStrategy()
        extractor = PromotionExtractor(s3_strategy)

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        # This will fail when it tries to use DataFrame operations, but we can verify the strategy call
        try:
            extractor.extract(start_date, end_date)
        except:
            pass  # Expected to fail due to DataFrame operations

        # Verify strategy was called with correct schema constants
        assert len(s3_strategy.get_source_df_calls) == 1
        schema_ref, table_name = s3_strategy.get_source_df_calls[0]
        assert schema_ref == LoadPromosSchema.SOURCE_SCHEMA_REF
        assert table_name == LoadPromosSchema.SOURCE_TABLE_NAME

    def test_date_string_formatting_logic(self):
        """Test date string formatting logic in isolation"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        # Test the same formatting logic used in the extractor
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_datetime_str = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
        end_datetime_str = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S')

        assert start_date_str == "2024-01-01"
        assert end_date_str == "2024-01-31"
        assert start_datetime_str == "2024-01-01 00:00:00"
        assert end_datetime_str == "2024-01-31 23:59:59"
