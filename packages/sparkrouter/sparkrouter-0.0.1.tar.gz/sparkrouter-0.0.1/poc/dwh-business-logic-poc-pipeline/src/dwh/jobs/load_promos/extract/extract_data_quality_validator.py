from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from dwh.services.data.threshold_evaluator import ThresholdEvaluator, ValidationThreshold, ThresholdOperator


class ExtractDataQualityValidator:
    """In-memory validation of raw extracted data"""

    def __init__(self, threshold_evaluator: ThresholdEvaluator):
        self.threshold_evaluator = threshold_evaluator
        self.name = "Extract Data Quality"

    def validate(self, df: DataFrame) -> None:
        """Validate raw data integrity - schema, nulls, basic constraints"""
        # try:
        # Row count validation with thresholds
        row_count = df.count()
        row_count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Row Count", row_count, row_count_thresholds
        )

        # Required fields validation
        self._validate_required_fields(df)

        # Null ID validation with thresholds
        null_id_count = df.filter(col("_id").isNull()).count()
        null_id_thresholds = [
            ValidationThreshold("green", ThresholdOperator.EQUAL_TO, 0),
            ValidationThreshold("red", ThresholdOperator.GREATER_THAN, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Null IDs", null_id_count, null_id_thresholds
        )

    def _validate_required_fields(self, df: DataFrame):
        """Validate required fields exist"""
        required_fields = ["_id", "updatedate", "ptn_ingress_date"]
        missing_fields = [field for field in required_fields if field not in df.columns]

        missing_fields_thresholds = [ValidationThreshold("red", ThresholdOperator.GREATER_THAN, 0, should_throw=True)]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - missing fields", len(missing_fields), missing_fields_thresholds
        )
