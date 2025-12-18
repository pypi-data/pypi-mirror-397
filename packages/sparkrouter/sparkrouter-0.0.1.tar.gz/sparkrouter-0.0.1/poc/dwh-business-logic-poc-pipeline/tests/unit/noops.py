"""
Centralized Noop implementations for unit testing.

This module contains all Noop/Mock classes used across unit tests to avoid duplication
and provide consistent test doubles.
"""
from typing import Dict, Any

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType

from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy
from dwh.services.data_sink.data_sink_strategy_factory import DataSinkStrategyFactory
from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.services.data_source.data_source_strategy_factory import DataSourceStrategyFactory
from dwh.services.email.email_service import NoopEmailService, EmailService
from dwh.services.email.email_service_factory import EmailServiceFactory
from dwh.services.file.ddl_file_reader import DDLFileReader
from dwh.services.notification.notification_service import NoopNotificationService, NotificationService
from dwh.services.notification.notification_service_factory import NotificationServiceFactory
from dwh.services.schema.schema_service import SchemaService
from dwh.services.schema.schema_service_factory import SchemaServiceFactory
from dwh.services.spark.spark_session_factory import SparkSessionFactory
from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService
from dwh.services.database.jdbc.jdbc_connection_service_factory import JdbcConnectionServiceFactory


class NoopSparkSession(SparkSession):
    """Minimal Noop implementation of SparkSession for unit testing"""
    
    def __init__(self):
        self.dataframes = []
    
    def createDataFrame(self, data, schema=None):
        """Create a NoopDataFrame instead of real Spark DataFrame"""
        noop_df = NoopDataFrame(data)
        self.dataframes.append(noop_df)
        return noop_df


class NoopSparkFactory(SparkSessionFactory):
    """Noop SparkSessionFactory for unit testing"""
    @staticmethod
    def create_spark_session(**kwargs):
        return NoopSparkSession()


class NoopDataFrame:
    """A minimal implementation of a Spark DataFrame for testing"""

    def __init__(self, data):
        self.data = data or []
        self.shown = False

    def show(self, n=20, truncate=True):
        self.shown = True
    
    def printSchema(self):
        pass
    
    def filter(self, condition):
        """Return empty DataFrame for null checks"""
        return NoopDataFrame([])
    
    def collect(self):
        """Return the data"""
        return self.data
    
    def count(self):
        """Return count of data"""
        return len(self.data)
    
    def isNull(self):
        """Return self for chaining"""
        return self
    
    def __getitem__(self, key):
        """Support column access like df['column']"""
        return NoopColumn(key)
    

    
    @property
    def columns(self):
        """Return required columns for validation"""
        return ['promotionid', 'promotiontype', 'etl_created_by']
    
    def __contains__(self, item):
        """Support 'column' in df checks"""
        return item in self.columns


class NoopColumn:
    """Noop column for DataFrame operations"""
    
    def __init__(self, name):
        self.name = name
    
    def isNull(self):
        return self


class NoopSourceStrategy(DataSourceStrategy):

    def get_type(self):
        return "NOOP"

    def get_source_df(self, schema_ref: str, table_name: str) -> DataFrame:
        return NoopDataFrame([])


class NoopDataSourceStrategyFactory(DataSourceStrategyFactory):
    """Noop DataSourceStrategyFactory for unit testing"""
    @staticmethod
    def create_data_source_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> DataSourceStrategy:
        return NoopSourceStrategy()


class NoopSinkStrategy(DataSinkStrategy):

    def get_type(self):
        pass

    def write_sink_df(self, df: DataFrame, schema_ref: str, sink_table: str, mode: str = "overwrite", **kwargs) -> None:
        pass


class NoopDataSinkStrategyFactory(DataSinkStrategyFactory):
    """Noop DataSinkStrategyFactory for unit testing"""
    @staticmethod
    def create_data_sink_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> DataSinkStrategy:
        return NoopSinkStrategy()


class NoopNotificationServiceFactory(NotificationServiceFactory):
    """Noop NotificationServiceFactory for unit testing"""
    @staticmethod
    def create_notification_service(config: Dict[str, Any]) -> NotificationService:
        return ValidatingNoopNotificationService()


class NoopEmailServiceFactory(EmailServiceFactory):
    """A no-op implementation of EmailServiceFactory for testing."""

    @staticmethod
    def create_email_service(config: Dict[str, Any]) -> EmailService:
        """Create a NoopEmailService for testing."""
        return NoopEmailService()


class NoopSchemaService(SchemaService):
    """"""

    def get_schema(self, schema_ref: str, table_name: str) -> StructType:
        pass


class ValidatingNoopNotificationService(NoopNotificationService):
    """Testable notification service that tracks calls"""
    
    def __init__(self):
        super().__init__()
        self._called = False
        self._last_message = ""
    
    def send_notification(self, message: str, **kwargs):
        self._called = True
        self._last_message = message
    
    def was_called(self) -> bool:
        return self._called
    
    @property
    def last_message(self) -> str:
        return self._last_message


class ValidatingNoopDataSourceStrategy(NoopSourceStrategy):
    """Testable data source strategy for unit testing"""
    
    def __init__(self):
        super().__init__()
        self._empty_result = False
        self._test_data = []
    
    def set_empty_result(self, empty: bool):
        self._empty_result = empty
    
    def set_test_data(self, data: list):
        self._test_data = data
    
    def get_source_df(self, schema_ref: str, table_name: str) -> DataFrame:
        if self._empty_result:
            return NoopDataFrame([])
        return NoopDataFrame(self._test_data if self._test_data else [])


class ValidatingNoopDataSinkStrategy(NoopSinkStrategy):
    """Testable data sink strategy for unit testing"""
    
    def __init__(self):
        super().__init__()
        self._write_failure = False
    
    def set_write_failure(self, should_fail: bool):
        self._write_failure = should_fail
    
    def write_sink_df(self, df: DataFrame, schema_ref: str, sink_table: str, mode: str = "overwrite", **kwargs) -> None:
        if self._write_failure:
            raise Exception("Failed to write to Unity Catalog")
    
    def execute_sql(self, sql: str) -> None:
        """Noop SQL execution for testing"""
        if self._write_failure:
            raise Exception("Failed to execute SQL")


class ValidatingNoopSchemaService(NoopSchemaService):
    """Testable schema service for unit testing"""
    
    def __init__(self):
        super().__init__()
        self._validation_failure = False
    
    def set_validation_failure(self, should_fail: bool):
        self._validation_failure = should_fail
    
    def get_schema(self, schema_ref: str, table_name: str) -> StructType:
        if self._validation_failure:
            raise ValueError("Schema validation failed")
        return StructType([])


class NoopSchemaServiceFactory(SchemaServiceFactory):
    """Noop SchemaServiceFactory for unit testing"""
    @staticmethod
    def create_schema_service(file_reader: DDLFileReader, schema_service_type: str = "DDL") -> SchemaService:
        return ValidatingNoopSchemaService()


class NoopJdbcConnectionService(JdbcConnectionService):
    """Noop JDBC connection service for unit testing"""
    
    def connect(self):
        """No-op connect"""
        pass
    
    def execute_query(self, sql: str, params: dict = None):
        """Return empty result for testing"""
        return []
    
    def close(self):
        """No-op close"""
        pass


class NoopJdbcConnectionServiceFactory(JdbcConnectionServiceFactory):
    """Noop JdbcConnectionServiceFactory for unit testing"""
    @staticmethod
    def create_connection(config: Dict[str, Any], spark_session=None) -> JdbcConnectionService:
        return NoopJdbcConnectionService()


class NoopThresholdEvaluator:
    """Noop ThresholdEvaluator for unit testing"""
    
    def evaluate_thresholds(self, metric_name: str, value: Any, thresholds: list) -> None:
        """No-op threshold evaluation"""
        pass


class NoopDatabaseLoadStrategy:
    """Noop DatabaseLoadStrategy for unit testing"""
    
    def load(self) -> None:
        """No-op load operation"""
        pass


class ValidatingNoopJDBCDataSinkStrategy(ValidatingNoopDataSinkStrategy):
    """Testable JDBC data sink strategy for unit testing"""
    
    def execute_sql(self, sql: str) -> None:
        """Noop SQL execution for testing"""
        if self._write_failure:
            raise Exception("Failed to execute SQL")