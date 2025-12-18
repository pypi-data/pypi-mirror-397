"""
New RedshiftLoader implementation with database strategy pattern
"""
from abc import ABC, abstractmethod

from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.services.data_sink.jdbc_data_sink_strategy import JDBCDataSinkStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class DatabaseLoadStrategy(ABC):
    """Abstract strategy for database-specific loading"""
    
    @abstractmethod
    def load(self) -> None:
        """Load data from S3 staging to final database table"""
        pass


class RedshiftLoadStrategy(DatabaseLoadStrategy):
    """Redshift-specific loading using COPY + MERGE"""
    
    def __init__(self, jdbc_sink_strategy: JDBCDataSinkStrategy, s3_staging_path: str, s3_source_strategy: DataSourceStrategy, aws_credentials: dict = None):
        self.jdbc_sink_strategy = jdbc_sink_strategy
        self.s3_staging_path = s3_staging_path
        self.s3_source_strategy = s3_source_strategy
        self.aws_credentials = aws_credentials or {}
    
    def load(self) -> None:
        """Load data from S3 to Redshift using COPY + MERGE"""
        # 1. COPY from S3 to staging table
        self._copy_from_s3_to_staging()
        
        # 2. MERGE from staging to core table
        self._execute_native_upsert()

    def _copy_from_s3_to_staging(self) -> None:
        """Execute Redshift COPY command from S3 to staging table"""
        # Build credentials clause
        if 'iam_role' in self.aws_credentials:
            credentials_clause = f"IAM_ROLE '{self.aws_credentials['iam_role']}'"
        else:
            access_key = self.aws_credentials.get('aws_access_key_id', '')
            secret_key = self.aws_credentials.get('aws_secret_access_key', '')
            credentials_clause = f"CREDENTIALS 'aws_access_key_id={access_key};aws_secret_access_key={secret_key}'"
        
        copy_sql = f"""
        COPY {LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME}
        FROM '{self.s3_staging_path}'
        {credentials_clause}
        FORMAT AS PARQUET;
        """
        
        self.jdbc_sink_strategy.execute_sql(copy_sql)
    
    def _execute_native_upsert(self) -> None:
        """Execute native Redshift MERGE statement for UPSERT operation"""
        upsert_sql = f"""
        MERGE INTO {LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME} AS target
        USING {LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME} AS source
        ON target.promotionid = source.promotionid
        WHEN MATCHED THEN
            UPDATE SET
                promotioncode = source.promotioncode,
                promotiondescription = source.promotiondescription,
                promotiontype = source.promotiontype,
                etl_created_at = CURRENT_TIMESTAMP,
                etl_created_by = source.etl_created_by
        WHEN NOT MATCHED THEN
            INSERT (promotionid, promotioncode, promotiondescription, promotiontype, 
                    etl_created_at, etl_created_by)
            VALUES (source.promotionid, source.promotioncode, source.promotiondescription, 
                    source.promotiontype, CURRENT_TIMESTAMP, source.etl_created_by);
        """
        
        self.jdbc_sink_strategy.execute_sql(upsert_sql)


class PostgresLoadStrategy(DatabaseLoadStrategy):
    """Postgres-specific loading using direct JDBC UPSERT"""
    
    def __init__(self, jdbc_sink_strategy: JDBCDataSinkStrategy, s3_source_strategy: DataSourceStrategy):
        self.jdbc_sink_strategy = jdbc_sink_strategy
        self.s3_source_strategy = s3_source_strategy
    
    def load(self) -> None:
        """Load data from S3 to Postgres via DataFrame read then JDBC UPSERT"""
        df = self.s3_source_strategy.get_source_df(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        
        self.jdbc_sink_strategy.write_sink_df(
            df,
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            mode="upsert"
        )


class NewRedshiftLoader:
    """Loads from S3 staging to database using strategy pattern"""
    
    def __init__(self, database_load_strategy: DatabaseLoadStrategy):
        self.database_load_strategy = database_load_strategy
    
    def load(self) -> None:
        """Load data from S3 staging to database"""
        self.database_load_strategy.load()
