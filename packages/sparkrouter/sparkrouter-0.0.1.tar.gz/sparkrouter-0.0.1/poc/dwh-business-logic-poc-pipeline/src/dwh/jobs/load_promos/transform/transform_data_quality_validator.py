from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from dwh.services.data.threshold_evaluator import ThresholdEvaluator, ValidationThreshold, ThresholdOperator


class TransformDataQualityValidator:
    """In-memory validation of transformed data"""

    def __init__(self, threshold_evaluator: ThresholdEvaluator):
        self.threshold_evaluator = threshold_evaluator
        self.name = "Transform Data Quality"

    def validate(self, df: DataFrame) -> None:
        """Validate transformed data - business rules, relationships, completeness"""
        # Row count validation
        row_count = df.count()
        row_count_thresholds = [
            ValidationThreshold("green", ThresholdOperator.GREATER_THAN, 0),
            ValidationThreshold("red", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Row Count", row_count, row_count_thresholds
        )

        # Null promotion ID validation
        null_promotion_ids = df.filter(col("promotionid").isNull()).count()
        null_id_thresholds = [
            ValidationThreshold("green", ThresholdOperator.EQUAL_TO, 0),
            ValidationThreshold("red", ThresholdOperator.GREATER_THAN, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Null Promotion IDs", null_promotion_ids, null_id_thresholds
        )

        # Duplicate validation
        total_count = df.count()
        distinct_count = df.select("promotionid").distinct().count()
        duplicate_count = total_count - distinct_count
        duplicate_thresholds = [
            ValidationThreshold("green", ThresholdOperator.EQUAL_TO, 0),
            ValidationThreshold("red", ThresholdOperator.GREATER_THAN, 0, should_throw=True)
        ]
        self.threshold_evaluator.evaluate_thresholds(
            f"{self.name} - Duplicates", duplicate_count, duplicate_thresholds
        )
