from pyspark.sql import DataFrame
from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class StageLoader:
    """Loads transformed data to S3 staging area for Redshift COPY operations"""
    
    def __init__(self, s3_sink_strategy: DataSinkStrategy):
        self.s3_sink_strategy = s3_sink_strategy
    
    def load(self, df: DataFrame) -> None:
        """Load DataFrame to S3 staging area as parquet"""
        # Convert TIME columns from Unity format to database format
        converted_df = self._convert_time_columns_for_database(df)
        
        # Write to S3 staging location for Redshift COPY
        self.s3_sink_strategy.write_sink_df(
            converted_df, 
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            mode="overwrite"
        )
    
    def _convert_time_columns_for_database(self, df: DataFrame) -> DataFrame:
        """Convert TIME columns from Unity format to database-compatible HH:MM:SS strings
        
        Unity TIME format: String seconds since midnight (e.g., "0", "86399000")
        Database TIME format: HH:MM:SS string format (e.g., "00:00:00", "23:59:59")
        
        This conversion is necessary because:
        - Unity stores TIME as seconds-since-midnight strings
        - Database TIME columns expect HH:MM:SS format
        - Spark handles TIME fields as StringType (no native TIME type)
        """
        from pyspark.sql.functions import when, col, format_string, floor
        
        # Known TIME columns that need conversion for this job
        time_columns = ['dailystarttime', 'dailyendtime']
        
        converted_df = df
        for col_name in time_columns:
            if col_name in df.columns:
                # Convert seconds-since-midnight to HH:MM:SS format
                # - Only converts numeric strings (Unity format)
                # - Caps hours at 23 to handle edge cases (e.g., 86399000 seconds = 23:59:59)
                # - Non-numeric values (already in HH:MM:SS format) are preserved
                converted_df = converted_df.withColumn(
                    col_name,
                    when(col(col_name).rlike(r'^\d+$'),  # Only convert numeric strings
                         format_string("%02d:%02d:%02d",  # Format as HH:MM:SS
                                     when(floor(col(col_name).cast("int") / 3600) > 23, 23)
                                     .otherwise(floor(col(col_name).cast("int") / 3600)),  # hours (max 23)
                                     floor((col(col_name).cast("int") % 3600) / 60),  # minutes
                                     col(col_name).cast("int") % 60  # seconds
                                     )
                    ).otherwise(col(col_name))  # Preserve non-numeric values
                )
        
        return converted_df
        
        print("Stage load completed: Data written to S3 staging area")
