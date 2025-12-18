from typing import Any
from dwh.jobs.abstract_job import AbstractJob
from dwh.jobs.load_promos.job_utils import JobUtils
from dwh.jobs.load_promos.extract.promotion_extractor import PromotionExtractor
from dwh.jobs.load_promos.extract.extract_data_quality_validator import ExtractDataQualityValidator
from dwh.jobs.load_promos.load.new_redshift_loader import DatabaseLoadStrategy
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.transform.transform_data_quality_validator import TransformDataQualityValidator
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load.unity_data_quality_validator import UnityDataQualityValidator
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from dwh.jobs.load_promos.load.stage_data_quality_validator import StageDataQualityValidator
from dwh.jobs.load_promos.load.redshift_data_quality_validator import RedshiftDataQualityValidator
from dwh.services.notification.notification_service import NotificationService


class LoadPromosJob(AbstractJob):    
    """
    LoadPromosJob - Modern ETL Pipeline with Single Responsibility Components
    
    CURRENT ARCHITECTURE (Clean Separation of Concerns):
    
    1. EXTRACT PHASE
       PromotionExtractor → ExtractDataQualityValidator
       • Reads promotion data from S3 parquet files
       • Validates raw data integrity (schema, nulls, basic constraints)
       • In-memory validation - no intermediate storage
    
    2. TRANSFORM PHASE  
       PromotionTransformer → TransformDataQualityValidator
       • Flattens nested structures, applies business rules
       • Validates transformed data (business rules, relationships)
       • In-memory validation - no intermediate storage
    
    3. LOAD PHASE (Independent Loaders)
       a) UnityLoader → UnityDataQualityValidator
          • Writes to Unity Catalog with Delta merge operations
          • Validates Unity Catalog data integrity
          
       b) StageLoader → StageDataQualityValidator  
          • Writes transformed data to S3 staging area as parquet
          • Validates staged data exists and is readable
          • Prepares data for Redshift COPY operations
          
       c) DatabaseLoadStrategy → RedshiftDataQualityValidator
          • Uses strategy pattern for different database targets:
          
          PostgresLoadStrategy:
          - Reads staged S3 data via stage_source_strategy
          - Transforms data in Spark/memory
          - Writes directly via JDBC to Postgres tables
          
          RedshiftLoadStrategy:
          - Validates staged S3 data exists via stage_source_strategy  
          - Executes native COPY command from S3 → Redshift staging
          - Executes MERGE/UPSERT from staging → core tables
    
    EXECUTION FLOW:
    S3 Source → Extract → Extract DQ → Transform → Transform DQ → 
    ├── Unity Load → Unity DQ
    ├── Stage Load → Stage DQ → Database Load → Database DQ
    
    KEY DESIGN PRINCIPLES:
    • Single Responsibility: Each component has one clear purpose
    • Strategy Pattern: DatabaseLoadStrategy adapts to different databases
    • In-Memory Validation: No intermediate storage until final destinations
    • Independent Loaders: Unity, Staging, and Database loads are decoupled
    • Fail Fast: Validation happens before expensive operations
    """

    def __init__(
            self,
            alarm_service: NotificationService,
            success_service: NotificationService,
            
            promotion_extractor: PromotionExtractor,
            extract_dq_validator: ExtractDataQualityValidator,
            
            promotion_transformer: PromotionTransformer,
            transform_dq_validator: TransformDataQualityValidator,
            
            unity_loader: UnityLoader,
            unity_dq_validator: UnityDataQualityValidator,

            stage_loader: StageLoader,
            stage_dq_validator: StageDataQualityValidator,
            
            redshift_loader: DatabaseLoadStrategy,
            redshift_dq_validator: RedshiftDataQualityValidator
    ):
        if not isinstance(alarm_service, NotificationService):
            raise ValueError('alarm_service must be instance of NotificationService')
        if not isinstance(success_service, NotificationService):
            raise ValueError('success_service must be instance of NotificationService')

        self.alarm_service = alarm_service
        self.success_service = success_service
        self.promotion_extractor = promotion_extractor
        self.extract_dq_validator = extract_dq_validator
        
        self.promotion_transformer = promotion_transformer
        self.transform_dq_validator = transform_dq_validator
        
        self.unity_loader = unity_loader
        self.unity_dq_validator = unity_dq_validator
        
        self.stage_loader = stage_loader
        self.stage_dq_validator = stage_dq_validator
        
        self.redshift_loader = redshift_loader
        self.redshift_dq_validator = redshift_dq_validator

    def execute_job(self, start_date: str, end_date: str, created_by: str) -> Any:
        start_date = JobUtils.parse_date_to_datetime(start_date, "start_date")
        end_date = JobUtils.parse_date_to_datetime(end_date, "end_date")

        if not created_by:
            raise ValueError("created_by parameter is required")

        # Extract Phase
        raw_df = self.promotion_extractor.extract(start_date, end_date)
        self.extract_dq_validator.validate(raw_df)

        # Transform Phase
        transformed_df = self.promotion_transformer.transform(raw_df, created_by)
        self.transform_dq_validator.validate(transformed_df)

        # Load Phase - Sequential loading
        print("Starting Unity Catalog load...")
        self.unity_loader.load(transformed_df)
        self.unity_dq_validator.validate(start_date, end_date)
        print("Unity Catalog load completed")

        print("Starting Stage load...")
        self.stage_loader.load(transformed_df)
        self.stage_dq_validator.validate(start_date, end_date)
        print("Stage load completed")

        # the following can be split off to a separate if as needed (no redshift access from databricks)

        print("Starting Redshift load...")
        self.redshift_loader.load()
        self.redshift_dq_validator.validate(start_date, end_date)
        print("Redshift load completed")
        
        return "LoadPromosJob completed successfully"

    def on_success(self, results: str) -> None:
        try:
            subject = "LoadPromosJob: Job Execution Successful"
            self.success_service.send_notification(subject=subject, message=results)
        except Exception as e:
            raise RuntimeError(f"Failed to send notification: {e}") from e

    def on_failure(self, error_message) -> None:
        try:
            subject = "LoadPromosJob: Job Execution Failed"
            self.alarm_service.send_notification(subject=subject, message=error_message)
        except Exception as e:
            raise RuntimeError(f"Failed to send notification: {e}") from e
