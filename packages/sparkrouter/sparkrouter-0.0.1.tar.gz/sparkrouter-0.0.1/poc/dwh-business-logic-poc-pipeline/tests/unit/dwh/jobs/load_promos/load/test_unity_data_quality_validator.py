import pytest
from dwh.jobs.load_promos.load.unity_data_quality_validator import UnityDataQualityValidator
from unit.noops import ValidatingNoopDataSourceStrategy, NoopThresholdEvaluator


class TestUnityDataQualityValidator:
    """Unit tests for UnityDataQualityValidator"""

    @pytest.fixture
    def source_strategy(self):
        return ValidatingNoopDataSourceStrategy()

    @pytest.fixture
    def threshold_evaluator(self):
        return NoopThresholdEvaluator()

    def test_init_with_valid_dependencies(self, source_strategy, threshold_evaluator):
        """Test validator initialization with valid dependencies"""
        validator = UnityDataQualityValidator(source_strategy, threshold_evaluator)
        assert validator.unity_source_strategy is source_strategy
        assert validator.threshold_evaluator is threshold_evaluator

    def test_init_stores_dependencies(self, source_strategy, threshold_evaluator):
        """Test that constructor properly stores all dependencies"""
        validator = UnityDataQualityValidator(source_strategy, threshold_evaluator)
        assert hasattr(validator, 'unity_source_strategy')
        assert hasattr(validator, 'threshold_evaluator')
        assert validator.unity_source_strategy == source_strategy
        assert validator.threshold_evaluator == threshold_evaluator