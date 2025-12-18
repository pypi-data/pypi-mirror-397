from abc import ABC, abstractmethod
from pyspark.sql import DataFrame


class DataSinkStrategy(ABC):

    @abstractmethod
    def get_type(self):
        """Get the strategy type."""
        pass

    @abstractmethod
    def write_sink_df(self, df: DataFrame, schema_ref: str, sink_table: str, mode: str = "overwrite", **kwargs) -> None:
        """Write a DataFrame to the specified sink table."""
        pass
