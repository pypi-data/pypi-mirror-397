from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.schemas.schema_upgrade_job import SchemaUpgradeJob
from dwh.services.database.jdbc.jdbc_connection_service_factory import JdbcConnectionServiceFactory
from dwh.services.file.file_locator_factory import FileLocatorFactory
from dwh.services.notification.notification_service_factory import NotificationServiceFactory
from dwh.services.spark.spark_session_factory import SparkSessionFactory


class SchemaUpgradeJobFactory(AbstractJobFactory):
    """
    Factory for creating SchemaUpgradeJob instances.
    """
    
    def __init__(self,
                 notification_service_factory=None,
                 file_locator_factory=None,
                 jdbc_connection_service_factory=None,
                 spark_session_factory=None,
                 **kwargs):
        """
        Initialize the factory with dependencies.
        
        :param notification_service_factory: Factory for creating notification services
        :param file_locator_factory: Factory for creating file locators
        :param jdbc_connection_service_factory: Factory for creating JDBC connections
        :param spark_session_factory: Factory for creating Spark sessions
        :param kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.notification_service_factory = notification_service_factory or NotificationServiceFactory
        self.file_locator_factory = file_locator_factory or FileLocatorFactory
        self.jdbc_connection_service_factory = jdbc_connection_service_factory or JdbcConnectionServiceFactory
        self.spark_session_factory = spark_session_factory or SparkSessionFactory

    def create_job(self, **kwargs) -> SchemaUpgradeJob:
        """
        Create a SchemaUpgradeJob instance.
        
        :param kwargs: Job configuration parameters
        :return: SchemaUpgradeJob instance
        """
        config = self.parse_job_config(job_name='schema_upgrade_job', **kwargs)
        print("Configuration for SchemaUpgradeJob:", config)

        try:
            alarm_config = config['alarm_service']
            alarm_service = self.notification_service_factory.create_notification_service(
                config=alarm_config
            )

            ddl_file_config = config.get('ddl_file_service', {})
            ddl_file_service = self.file_locator_factory.create_file_locator(config=ddl_file_config)

            # todo: wrap this logic in a utility function
            #  with full explanation as to how this value gets set in entry_point.py
            has_spark = kwargs.get('has_spark', False)
            spark_session = None
            if isinstance(has_spark, str):
                # Convert string to boolean
                # todo: does this seem too forgiving?
                has_spark = has_spark.lower() in ['true', '1', 'yes']

            postgres_config = config['postgres_connection']
            if has_spark and not postgres_config.get('force_direct_connection', False):
                spark_session = self.spark_session_factory.create_spark_session(**kwargs)

            postgres_service = self.jdbc_connection_service_factory.create_connection(
                config=postgres_config,
                spark_session=spark_session,
            )

            return SchemaUpgradeJob(
                alarm_service=alarm_service,
                ddl_file_service=ddl_file_service,
                postgres_service=postgres_service
            )

        except KeyError as e:
            # todo: utility to display configuration expectations
            raise ValueError(f"Missing required configuration key: {e}")


def main(**kwargs):
    operator = SchemaUpgradeJobFactory(**kwargs)
    return operator.run(**kwargs)
