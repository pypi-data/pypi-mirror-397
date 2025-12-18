"""
Unit tests for ThresholdEvaluator
"""
import pytest

from dwh.services.data.threshold_evaluator import (
    ThresholdEvaluator,
    ThresholdOperator,
    ValidationThreshold
)
from dwh.services.notification.notification_service import NoopNotificationService


class TestThresholdOperator:
    """Test ThresholdOperator enum values"""

    def test_operator_values(self):
        """Test all operator enum values are correct"""
        assert ThresholdOperator.EQUAL_TO.value == "=="
        assert ThresholdOperator.GREATER_THAN.value == ">"
        assert ThresholdOperator.GREATER_THAN_OR_EQUAL.value == ">="
        assert ThresholdOperator.LESS_THAN.value == "<"
        assert ThresholdOperator.LESS_THAN_OR_EQUAL.value == "<="


class TestValidationThreshold:
    """Test ValidationThreshold dataclass"""

    def test_basic_threshold_creation(self):
        """Test creating basic threshold"""
        threshold = ValidationThreshold(
            name="test_threshold",
            operator=ThresholdOperator.GREATER_THAN,
            value=100
        )
        
        assert threshold.name == "test_threshold"
        assert threshold.operator == ThresholdOperator.GREATER_THAN
        assert threshold.value == 100
        assert threshold.should_throw is False

    def test_threshold_with_should_throw(self):
        """Test creating threshold with should_throw=True"""
        threshold = ValidationThreshold(
            name="critical_threshold",
            operator=ThresholdOperator.LESS_THAN,
            value=0,
            should_throw=True
        )
        
        assert threshold.should_throw is True


class TestThresholdEvaluator:
    """Test ThresholdEvaluator service"""

    def test_init(self):
        """Test ThresholdEvaluator initialization"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        assert evaluator.notification_service is notification_service

    def test_evaluate_threshold_equal_to_true(self):
        """Test _evaluate_threshold with EQUAL_TO operator - threshold met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.EQUAL_TO, 100)
        result = evaluator._evaluate_threshold(100, threshold)
        
        assert result is True

    def test_evaluate_threshold_equal_to_false(self):
        """Test _evaluate_threshold with EQUAL_TO operator - threshold not met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.EQUAL_TO, 100)
        result = evaluator._evaluate_threshold(99, threshold)
        
        assert result is False

    def test_evaluate_threshold_greater_than_true(self):
        """Test _evaluate_threshold with GREATER_THAN operator - threshold met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.GREATER_THAN, 100)
        result = evaluator._evaluate_threshold(101, threshold)
        
        assert result is True

    def test_evaluate_threshold_greater_than_false(self):
        """Test _evaluate_threshold with GREATER_THAN operator - threshold not met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.GREATER_THAN, 100)
        result = evaluator._evaluate_threshold(100, threshold)
        
        assert result is False

    def test_evaluate_threshold_greater_than_or_equal_true_greater(self):
        """Test _evaluate_threshold with GREATER_THAN_OR_EQUAL operator - greater value"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.GREATER_THAN_OR_EQUAL, 100)
        result = evaluator._evaluate_threshold(101, threshold)
        
        assert result is True

    def test_evaluate_threshold_greater_than_or_equal_true_equal(self):
        """Test _evaluate_threshold with GREATER_THAN_OR_EQUAL operator - equal value"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.GREATER_THAN_OR_EQUAL, 100)
        result = evaluator._evaluate_threshold(100, threshold)
        
        assert result is True

    def test_evaluate_threshold_greater_than_or_equal_false(self):
        """Test _evaluate_threshold with GREATER_THAN_OR_EQUAL operator - threshold not met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.GREATER_THAN_OR_EQUAL, 100)
        result = evaluator._evaluate_threshold(99, threshold)
        
        assert result is False

    def test_evaluate_threshold_less_than_true(self):
        """Test _evaluate_threshold with LESS_THAN operator - threshold met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.LESS_THAN, 100)
        result = evaluator._evaluate_threshold(99, threshold)
        
        assert result is True

    def test_evaluate_threshold_less_than_false(self):
        """Test _evaluate_threshold with LESS_THAN operator - threshold not met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.LESS_THAN, 100)
        result = evaluator._evaluate_threshold(100, threshold)
        
        assert result is False

    def test_evaluate_threshold_less_than_or_equal_true_less(self):
        """Test _evaluate_threshold with LESS_THAN_OR_EQUAL operator - less value"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.LESS_THAN_OR_EQUAL, 100)
        result = evaluator._evaluate_threshold(99, threshold)
        
        assert result is True

    def test_evaluate_threshold_less_than_or_equal_true_equal(self):
        """Test _evaluate_threshold with LESS_THAN_OR_EQUAL operator - equal value"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.LESS_THAN_OR_EQUAL, 100)
        result = evaluator._evaluate_threshold(100, threshold)
        
        assert result is True

    def test_evaluate_threshold_less_than_or_equal_false(self):
        """Test _evaluate_threshold with LESS_THAN_OR_EQUAL operator - threshold not met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("test", ThresholdOperator.LESS_THAN_OR_EQUAL, 100)
        result = evaluator._evaluate_threshold(101, threshold)
        
        assert result is False

    def test_evaluate_threshold_unknown_operator(self):
        """Test _evaluate_threshold with unknown operator raises ValueError"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        # Create threshold with invalid operator by bypassing enum
        threshold = ValidationThreshold("test", "invalid_operator", 100)
        
        with pytest.raises(ValueError, match="Unknown threshold operator"):
            evaluator._evaluate_threshold(100, threshold)

    def test_evaluate_thresholds_no_thresholds(self):
        """Test evaluate_thresholds with empty threshold list"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        # Should not raise any exceptions
        evaluator.evaluate_thresholds("test_check", 100, [])

    def test_evaluate_thresholds_threshold_not_met(self):
        """Test evaluate_thresholds when threshold is not met"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("warning", ThresholdOperator.GREATER_THAN, 100)
        
        # Should not raise any exceptions or send notifications
        evaluator.evaluate_thresholds("test_check", 50, [threshold])

    def test_evaluate_thresholds_threshold_met_no_throw(self):
        """Test evaluate_thresholds when threshold is met but should_throw=False"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("warning", ThresholdOperator.GREATER_THAN, 100)
        
        # Should send notification but not throw
        evaluator.evaluate_thresholds("test_check", 150, [threshold])

    def test_evaluate_thresholds_threshold_met_with_throw(self):
        """Test evaluate_thresholds when threshold is met and should_throw=True"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("critical", ThresholdOperator.GREATER_THAN, 100, should_throw=True)
        
        with pytest.raises(ValueError, match="test_check failed: test_check: 150 > 100"):
            evaluator.evaluate_thresholds("test_check", 150, [threshold])

    def test_evaluate_thresholds_multiple_thresholds_mixed(self):
        """Test evaluate_thresholds with multiple thresholds - some met, some not"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        thresholds = [
            ValidationThreshold("warning", ThresholdOperator.GREATER_THAN, 50),  # Met
            ValidationThreshold("info", ThresholdOperator.LESS_THAN, 200),      # Met
            ValidationThreshold("debug", ThresholdOperator.EQUAL_TO, 200)       # Not met
        ]
        
        # Should send notifications for first two thresholds but not throw
        evaluator.evaluate_thresholds("test_check", 100, thresholds)

    def test_evaluate_thresholds_multiple_thresholds_with_throw(self):
        """Test evaluate_thresholds with multiple thresholds where one should throw"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        thresholds = [
            ValidationThreshold("warning", ThresholdOperator.GREATER_THAN, 50),           # Met
            ValidationThreshold("critical", ThresholdOperator.GREATER_THAN, 80, True)    # Met and should throw
        ]
        
        with pytest.raises(ValueError, match="test_check failed: test_check: 100 > 80"):
            evaluator.evaluate_thresholds("test_check", 100, thresholds)

    def test_evaluate_thresholds_string_values(self):
        """Test evaluate_thresholds with string values"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("string_check", ThresholdOperator.EQUAL_TO, "expected")
        
        # Should send notification
        evaluator.evaluate_thresholds("string_test", "expected", [threshold])

    def test_evaluate_thresholds_float_values(self):
        """Test evaluate_thresholds with float values"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        threshold = ValidationThreshold("float_check", ThresholdOperator.GREATER_THAN, 99.5)
        
        # Should send notification
        evaluator.evaluate_thresholds("float_test", 100.1, [threshold])

    def test_evaluate_thresholds_exception_in_evaluation_bubbles_up(self):
        """Test that exceptions during threshold evaluation bubble up"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        # Create threshold with invalid operator
        threshold = ValidationThreshold("test", "invalid", 100)
        
        with pytest.raises(ValueError, match="Unknown threshold operator"):
            evaluator.evaluate_thresholds("test_check", 100, [threshold])


class TestThresholdEvaluatorIntegration:
    """Integration tests for ThresholdEvaluator with different scenarios"""

    def test_data_quality_check_scenario(self):
        """Test realistic data quality check scenario"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        # Simulate row count validation
        thresholds = [
            ValidationThreshold("min_rows", ThresholdOperator.GREATER_THAN, 1000),
            ValidationThreshold("max_rows", ThresholdOperator.LESS_THAN, 1000000),
            ValidationThreshold("zero_rows", ThresholdOperator.EQUAL_TO, 0, should_throw=True)
        ]
        
        # Test with normal row count - should only trigger min_rows notification
        evaluator.evaluate_thresholds("daily_sales_count", 50000, thresholds)

    def test_performance_threshold_scenario(self):
        """Test realistic performance threshold scenario"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        # Simulate execution time validation
        thresholds = [
            ValidationThreshold("slow_warning", ThresholdOperator.GREATER_THAN, 300),     # 5 minutes
            ValidationThreshold("timeout_error", ThresholdOperator.GREATER_THAN, 1800, True)  # 30 minutes
        ]
        
        # Test with slow but acceptable execution time
        evaluator.evaluate_thresholds("etl_execution_time", 600, thresholds)  # 10 minutes

    def test_business_rule_validation_scenario(self):
        """Test realistic business rule validation scenario"""
        notification_service = NoopNotificationService()
        evaluator = ThresholdEvaluator(notification_service)
        
        # Simulate revenue validation
        thresholds = [
            ValidationThreshold("revenue_drop", ThresholdOperator.LESS_THAN, 1000000, should_throw=True),
            ValidationThreshold("revenue_spike", ThresholdOperator.GREATER_THAN, 10000000)
        ]
        
        # Test with revenue drop that should throw
        with pytest.raises(ValueError, match="revenue_validation failed"):
            evaluator.evaluate_thresholds("revenue_validation", 500000, thresholds)