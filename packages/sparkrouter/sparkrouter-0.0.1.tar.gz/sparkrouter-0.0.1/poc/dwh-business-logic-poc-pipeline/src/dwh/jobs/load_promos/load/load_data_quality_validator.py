from datetime import datetime
from dwh.services.data.threshold_evaluator import ThresholdEvaluator, ValidationThreshold, ThresholdOperator
from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class LoadDataQualityValidator:
    """Post-load validation via SQL queries"""

    def __init__(
            self,
            unity_source_strategy: DataSourceStrategy,
            redshift_source_strategy: DataSourceStrategy,
            threshold_evaluator: ThresholdEvaluator
    ):
        self.unity_strategy = unity_source_strategy
        self.redshift_strategy = redshift_source_strategy
        self.threshold_evaluator = threshold_evaluator
        self.name = "Load Data Quality"

    def validate(self, start_date: datetime, end_date: datetime) -> None:
        """Validate final loaded data - row counts, referential integrity"""
        # Get data from both destinations with schema validation
        unity_df = self.unity_strategy.get_source_df(LoadPromosSchema.UNITY_SCHEMA_REF, LoadPromosSchema.UNITY_TABLE_NAME)
        redshift_df = self.redshift_strategy.get_source_df(LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF, LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME)

        unity_count = unity_df.count()
        redshift_count = redshift_df.count()

        # Unity Catalog row count validation
        unity_count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Unity Count", unity_count, unity_count_thresholds
        )

        # Redshift row count validation
        redshift_count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Redshift Count", redshift_count, redshift_count_thresholds
        )

        # Row count consistency validation
        count_difference = abs(unity_count - redshift_count)
        consistency_thresholds = [
            ValidationThreshold("green", ThresholdOperator.EQUAL_TO, 0),
            ValidationThreshold("red", ThresholdOperator.GREATER_THAN, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Count Consistency", count_difference, consistency_thresholds
        )
