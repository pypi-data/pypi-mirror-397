from pyspark.sql import DataFrame
from dwh.services.data_sink.jdbc_data_sink_strategy import JDBCDataSinkStrategy


class PostgresDataSinkStrategy(JDBCDataSinkStrategy):
    """Postgres-specific data sink strategy using direct JDBC writes"""
    
    def get_type(self) -> str:
        return "POSTGRES"
    
    def _write_dataframe(self, df: DataFrame, sink_table: str) -> None:
        """Write DataFrame directly to Postgres via JDBC"""
        # Write DataFrame directly to Postgres
        df.write \
            .format("jdbc") \
            .option("url", self.jdbc_url) \
            .option("dbtable", sink_table) \
            .option("user", self.properties.get("user")) \
            .option("password", self.properties.get("password")) \
            .option("driver", "org.postgresql.Driver") \
            .option("stringtype", "unspecified") \
            .mode("append") \
            .save()
