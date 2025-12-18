from typing import List, Any
from enum import Enum
from dataclasses import dataclass
from dwh.services.notification.notification_service import NotificationService


class ThresholdOperator(Enum):
    EQUAL_TO = "=="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="


@dataclass
class ValidationThreshold:
    name: str
    operator: ThresholdOperator
    value: Any
    should_throw: bool = False


class ThresholdEvaluator:
    """Service for evaluating thresholds and handling notifications"""

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def evaluate_thresholds(self, check_name: str, actual_value: Any, thresholds: List[ValidationThreshold]) -> None:
        """Evaluate thresholds and send notifications"""

        # print(f"{check_name} actual value: {actual_value}")
        for threshold in thresholds:
            try:
                threshold_met = self._evaluate_threshold(actual_value, threshold)
                # print(f"{check_name} threshold {'' if threshold_met else 'not'} met: {actual_value} {threshold.operator.value} {threshold.value}")

                if threshold_met:
                    message = f"{check_name}: {actual_value} {threshold.operator.value} {threshold.value}"

                    self.notification_service.send_notification(
                        f"{check_name} - {threshold.name}", message
                    )

                    if threshold.should_throw:
                        raise ValueError(f"{check_name} failed: {message}")
            except Exception as e:
                print(f"Error evaluating threshold: {e}")
                # bubble this error all the way up - job will be killed
                raise

    def _evaluate_threshold(self, actual: Any, threshold: ValidationThreshold) -> bool:
        """Evaluate if actual value meets threshold criteria"""
        if threshold.operator == ThresholdOperator.EQUAL_TO:
            return actual == threshold.value
        elif threshold.operator == ThresholdOperator.GREATER_THAN:
            return actual > threshold.value
        elif threshold.operator == ThresholdOperator.GREATER_THAN_OR_EQUAL:
            return actual >= threshold.value
        elif threshold.operator == ThresholdOperator.LESS_THAN:
            return actual < threshold.value
        elif threshold.operator == ThresholdOperator.LESS_THAN_OR_EQUAL:
            return actual <= threshold.value
        else:
            raise ValueError(f"Unknown threshold operator: {threshold.operator}")
