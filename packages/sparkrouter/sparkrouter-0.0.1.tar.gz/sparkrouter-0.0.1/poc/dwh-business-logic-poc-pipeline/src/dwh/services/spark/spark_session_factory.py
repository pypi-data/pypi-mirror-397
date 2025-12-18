class SparkSessionFactory:
    """Utility class for managing Spark sessions."""

    @staticmethod
    def create_spark_session(**kwargs):
        spark_service = kwargs.pop('service_provider', None)

        if spark_service == 'DATABRICKS':
            databricks_connection_name = kwargs.get('databricks_connection_name', None)
            if not databricks_connection_name:
                # todo: display all variables
                raise ValueError("Missing required argument: databricks_connection_name")

            # Get or create the SparkSession
            from pyspark.sql import SparkSession
            return SparkSession.builder.getOrCreate()
        elif spark_service == 'GLUE':
            from pyspark.context import SparkContext
            from awsglue.context import GlueContext

            # Initialize contexts
            sc = SparkContext()
            glueContext = GlueContext(sc)
            return glueContext.spark_session
        elif spark_service == 'CONTAINER':
            from pyspark.sql import SparkSession
            return SparkSession.builder \
                .appName("LocalSparkSession") \
                .config("spark.sql.shuffle.partitions", "2") \
                .getOrCreate()
        else:
            valid_types = ['DATABRICKS', 'GLUE', 'DOCKER']
            raise ValueError(f"Unsupported spark_service[{spark_service}]. Valid options are: {', '.join(valid_types)}")
