from datetime import datetime
from dwh.services.data.threshold_evaluator import ThresholdEvaluator, ValidationThreshold, ThresholdOperator
from dwh.services.data_source.data_source_strategy import DataSourceStrategy


class StageDataQualityValidator:
    """Validates S3 staged data exists and is readable"""
    
    def __init__(self, stage_source_strategy: DataSourceStrategy, threshold_evaluator: ThresholdEvaluator):
        self.stage_source_strategy = stage_source_strategy
        self.threshold_evaluator = threshold_evaluator
    
    def validate(self, start_date: datetime, end_date: datetime) -> None:
        """Validate staged data exists and is readable"""
        # Read staged data for validation
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        staged_df = self.stage_source_strategy.get_source_df(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        
        # Validate record count using threshold pattern
        record_count = staged_df.count()
        count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            "Stage Data Quality - Row Count", record_count, count_thresholds
        )
        
        # Validate data is readable and has expected structure
        required_fields = ['promotionid', 'promotiontype', 'etl_created_by']
        df_columns = staged_df.columns
        
        for field in required_fields:
            if field not in df_columns:
                raise ValueError(f"Stage validation failed: Required field {field} missing from staged data")
        
        print(f"Stage validation passed: {record_count} records staged and validated")
