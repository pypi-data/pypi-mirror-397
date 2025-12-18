from datetime import datetime
from dwh.services.data.threshold_evaluator import ThresholdEvaluator, ValidationThreshold, ThresholdOperator
from dwh.services.data_source.data_source_strategy import DataSourceStrategy


class RedshiftDataQualityValidator:
    """Validates Redshift data after database loading"""
    
    def __init__(self, redshift_source_strategy: DataSourceStrategy, threshold_evaluator: ThresholdEvaluator):
        self.redshift_source_strategy = redshift_source_strategy
        self.threshold_evaluator = threshold_evaluator
    
    def validate(self, start_date: datetime, end_date: datetime) -> None:
        """Validate Redshift core table data integrity"""
        # Read Redshift core data for validation
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        redshift_df = self.redshift_source_strategy.get_source_df(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF, 
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        
        # DEBUG: Show what data we have
        print(f"DEBUG REDSHIFT VALIDATOR: Found {redshift_df.count()} records")
        if redshift_df.count() > 0:
            print("DEBUG REDSHIFT VALIDATOR: Schema:")
            redshift_df.printSchema()
            print("DEBUG REDSHIFT VALIDATOR: Sample data:")
            redshift_df.show(5, truncate=False)
        
        # Validate record count using threshold pattern
        record_count = redshift_df.count()
        count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            "Redshift Data Quality - Row Count", record_count, count_thresholds
        )
        
        # Validate required fields
        required_fields = ['promotionid', 'promotiontype', 'etl_created_by']
        for field in required_fields:
            null_count = redshift_df.filter(redshift_df[field].isNull()).count()
            if null_count > 0:
                raise ValueError(f"Redshift validation failed: {null_count} null values in required field {field}")
        
        print(f"Redshift validation passed: {record_count} total records validated")
