from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_utc_timestamp

from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class PromotionExtractor:
    """Pure extraction from S3 parquet files - schema enforced at DataSourceStrategy level"""

    def __init__(self, s3_data_source_strategy: DataSourceStrategy):
        self.s3_data_source_strategy = s3_data_source_strategy

    def extract(self, start_date: datetime, end_date: datetime) -> DataFrame:
        """Extract promotion data from S3 parquet files with schema enforcement"""
        # Pass schema reference and table name for validation
        df = self.s3_data_source_strategy.get_source_df(
            schema_ref=LoadPromosSchema.SOURCE_SCHEMA_REF,
            table_name=LoadPromosSchema.SOURCE_TABLE_NAME
        )

        print(f"Extracted DataFrame with {df.count()} rows")

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_datetime_str = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
        end_datetime_str = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S')

        # Use lowercase field names that match test data
        df_filtered =  df.filter(
            (col("ptn_ingress_date").between(start_date_str, end_date_str))
            & (from_utc_timestamp(col("updatedate"), "America/Los_Angeles").cast("timestamp").between(
                start_datetime_str, end_datetime_str))
        )

        print(f"Filtered DataFrame with {df_filtered.count()} rows between {start_date_str} and {end_date_str}")

        return df_filtered
