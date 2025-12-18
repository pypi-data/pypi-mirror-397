from abc import ABC, abstractmethod

from pyspark.sql import DataFrame


class DataSourceStrategy(ABC):

    @abstractmethod
    def get_type(self):
        """Get the strategy type."""
        pass

    # todo: this is bad form passing in spark. Some instances need it, others do not

    @abstractmethod
    def get_source_df(self, schema_ref: str, table_name: str) -> DataFrame:
        """Get a DataFrame for the specified source table."""
        pass

    # @abstractmethod
    # def write_sink_df(self, df: DataFrame, sink_table, mode="overwrite", **kwargs):
    #     """Write a DataFrame to the specified sink table."""
    #     pass
