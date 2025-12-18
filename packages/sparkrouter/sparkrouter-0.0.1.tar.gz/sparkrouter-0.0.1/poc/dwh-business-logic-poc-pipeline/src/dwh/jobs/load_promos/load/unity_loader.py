from pyspark.sql import DataFrame

from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class UnityLoader:
    """Loads to Unity Catalog with schema validation"""

    def __init__(self, unity_strategy: DataSinkStrategy):
        self.unity_strategy = unity_strategy

    def load(self, df: DataFrame) -> None:
        """Load data to Unity Catalog as Delta table with schema validation"""
        self.unity_strategy.write_sink_df(df, LoadPromosSchema.UNITY_SCHEMA_REF, LoadPromosSchema.UNITY_TABLE_NAME, mode="overwrite")
