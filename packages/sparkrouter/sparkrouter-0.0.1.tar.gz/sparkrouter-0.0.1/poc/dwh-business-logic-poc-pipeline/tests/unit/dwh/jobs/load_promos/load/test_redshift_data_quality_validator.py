import pytest
from dwh.jobs.load_promos.load.redshift_data_quality_validator import RedshiftDataQualityValidator
from unit.noops import ValidatingNoopDataSourceStrategy, NoopThresholdEvaluator


class TestRedshiftDataQualityValidator:
    """Unit tests for RedshiftDataQualityValidator"""

    @pytest.fixture
    def source_strategy(self):
        return ValidatingNoopDataSourceStrategy()

    @pytest.fixture
    def threshold_evaluator(self):
        return NoopThresholdEvaluator()

    def test_init_with_valid_dependencies(self, source_strategy, threshold_evaluator):
        """Test validator initialization with valid dependencies"""
        validator = RedshiftDataQualityValidator(source_strategy, threshold_evaluator)
        assert validator.redshift_source_strategy is source_strategy
        assert validator.threshold_evaluator is threshold_evaluator

    def test_init_stores_dependencies(self, source_strategy, threshold_evaluator):
        """Test that constructor properly stores all dependencies"""
        validator = RedshiftDataQualityValidator(source_strategy, threshold_evaluator)
        assert hasattr(validator, 'redshift_source_strategy')
        assert hasattr(validator, 'threshold_evaluator')
        assert validator.redshift_source_strategy == source_strategy
        assert validator.threshold_evaluator == threshold_evaluator