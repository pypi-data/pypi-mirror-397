import pytest
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from unit.noops import ValidatingNoopDataSinkStrategy


class TestStageLoader:
    """Unit tests for StageLoader"""

    @pytest.fixture
    def sink_strategy(self):
        return ValidatingNoopDataSinkStrategy()

    def test_init_with_valid_strategy(self, sink_strategy):
        """Test StageLoader initialization with valid strategy"""
        loader = StageLoader(sink_strategy)
        assert loader.s3_sink_strategy is sink_strategy

    def test_init_stores_strategy_reference(self, sink_strategy):
        """Test that constructor properly stores strategy reference"""
        loader = StageLoader(sink_strategy)
        assert hasattr(loader, 's3_sink_strategy')
        assert loader.s3_sink_strategy == sink_strategy