from datetime import datetime
from dwh.services.data.threshold_evaluator import ThresholdEvaluator, ValidationThreshold, ThresholdOperator
from dwh.services.data_source.data_source_strategy import DataSourceStrategy


class UnityDataQualityValidator:
    """Validates Unity Catalog data after loading"""
    
    def __init__(self, unity_source_strategy: DataSourceStrategy, threshold_evaluator: ThresholdEvaluator):
        self.unity_source_strategy = unity_source_strategy
        self.threshold_evaluator = threshold_evaluator
    
    def validate(self, start_date: datetime, end_date: datetime) -> None:
        """Validate Unity Catalog data integrity"""
        # Read Unity data for validation
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        unity_df = self.unity_source_strategy.get_source_df(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        
        # Validate record count using threshold pattern
        record_count = unity_df.count()
        count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            "Unity Data Quality - Row Count", record_count, count_thresholds
        )
        
        # Validate required fields
        required_fields = ['promotionid', 'promotiontype', 'etl_created_by']
        for field in required_fields:
            null_count = unity_df.filter(unity_df[field].isNull()).count()
            if null_count > 0:
                raise ValueError(f"Unity Catalog validation failed: {null_count} null values in required field {field}")
        
        print(f"Unity Catalog validation passed: {record_count} records validated")
