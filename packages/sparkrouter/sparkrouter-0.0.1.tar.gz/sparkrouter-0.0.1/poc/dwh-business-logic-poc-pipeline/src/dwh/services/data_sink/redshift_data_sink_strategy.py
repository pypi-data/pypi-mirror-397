from pyspark.sql import DataFrame
from dwh.services.data_sink.jdbc_data_sink_strategy import JDBCDataSinkStrategy


class RedshiftDataSinkStrategy(JDBCDataSinkStrategy):
    """
    Redshift-specific data sink strategy that handles S3 staging internally.
    
    This strategy encapsulates the full Redshift loading pattern:
    1. Write DataFrame to S3 staging (parquet format)
    2. Execute Redshift COPY command from S3
    3. Handle all S3 operations internally
    """
    
    def __init__(self, spark, schema_service, jdbc_url: str, s3_staging_path: str, properties: dict, debug_schemas: bool = False):
        super().__init__(spark, schema_service, jdbc_url, properties, debug_schemas)
        self.s3_staging_path = s3_staging_path
        # self.s3_operations = []  # Track S3 operations for testing
    
    def get_type(self):
        return "REDSHIFT"
    
    def _write_dataframe(self, df: DataFrame, sink_table: str) -> None:
        """Write DataFrame to Redshift via S3 staging and COPY command"""
        # 1. Write to S3 staging
        s3_path = f"{self.s3_staging_path}/{sink_table.split('.')[-1]}"
        self._write_to_s3_staging(df, s3_path)
        
        # 2. Execute Redshift COPY command
        copy_sql = f"""
        COPY {sink_table} 
        FROM '{s3_path}' 
        IAM_ROLE 'arn:aws:iam::account:role/RedshiftRole'
        FORMAT AS PARQUET
        """.strip()
        
        self.execute_sql(copy_sql)
        print(f"REDSHIFT COPY: Executed COPY from {s3_path} to {sink_table}")
        
        # Track for testing
        # self.s3_operations.append({
        #     'operation': 'copy',
        #     'source': s3_path,
        #     'target': sink_table
        # })
    
    def _write_to_s3_staging(self, df: DataFrame, s3_path: str) -> None:
        """Write DataFrame to S3 staging area as parquet"""
        df.write.mode("overwrite").parquet(s3_path)
        
        # Track for testing
        # self.s3_operations.append({
        #     'operation': 'write',
        #     'path': s3_path,
        #     'row_count': df.count()
        # })
        
        print(f"REDSHIFT S3 STAGING: Wrote {df.count()} rows to {s3_path}")
