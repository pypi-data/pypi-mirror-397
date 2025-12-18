"""
Unit tests for UnityLoader
"""
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class NoopDataFrame:
    """Noop DataFrame for testing"""
    pass


class NoopDataSinkStrategy:
    """Noop DataSinkStrategy for unit testing"""

    def __init__(self):
        self.write_sink_df_calls = []

    def write_sink_df(self, df, schema_ref, sink_table, mode="overwrite", **kwargs):
        self.write_sink_df_calls.append((df, schema_ref, sink_table, mode, kwargs))


class TestUnityLoader:
    """Test UnityLoader class"""

    def test_init(self):
        """Test UnityLoader initialization"""
        unity_strategy = NoopDataSinkStrategy()
        loader = UnityLoader(unity_strategy=unity_strategy)
        
        assert loader.unity_strategy is unity_strategy

    def test_load_calls_strategy_with_schema_constants(self):
        """Test load calls strategy with correct schema constants"""
        unity_strategy = NoopDataSinkStrategy()
        loader = UnityLoader(unity_strategy=unity_strategy)

        noop_df = NoopDataFrame()
        loader.load(noop_df)

        # Verify strategy was called with correct schema constants
        assert len(unity_strategy.write_sink_df_calls) == 1
        call = unity_strategy.write_sink_df_calls[0]
        df, schema_ref, sink_table, mode, kwargs = call
        
        assert df is noop_df
        assert schema_ref == LoadPromosSchema.UNITY_SCHEMA_REF
        assert sink_table == LoadPromosSchema.UNITY_TABLE_NAME
        assert mode == "overwrite"
