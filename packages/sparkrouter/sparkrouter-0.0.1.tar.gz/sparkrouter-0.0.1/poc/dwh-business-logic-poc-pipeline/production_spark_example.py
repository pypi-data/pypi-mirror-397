"""
Example of creating Spark session for production using centralized configuration.

This demonstrates how to use SparkConfig in production environments
to ensure consistency with Docker and test environments.
"""

from spark_config import SparkConfig


def create_production_spark_session(app_name: str):
    """
    Create production Spark session with centralized configuration.
    
    Args:
        app_name: Name of the Spark application
        
    Returns:
        Configured SparkSession ready for production use
    """
    # Use centralized configuration for production
    spark = SparkConfig.create_production_session(app_name)
    
    print(f"Created production Spark session: {app_name}")
    print(f"Spark version: {spark.version}")
    print(f"Master: {spark.sparkContext.master}")
    
    return spark


def create_custom_spark_session(app_name: str, custom_configs: dict = None):
    """
    Create Spark session with custom configurations on top of base config.
    
    Args:
        app_name: Name of the Spark application
        custom_configs: Additional configurations to apply
        
    Returns:
        Configured SparkSession with custom settings
    """
    builder = SparkConfig.get_session_builder(app_name, "yarn")
    
    # Add custom configurations
    if custom_configs:
        for key, value in custom_configs.items():
            builder = builder.config(key, value)
    
    # Add production JAR paths
    jar_dir = "/opt/spark/jars"
    jar_paths = [f"{jar_dir}/{jar}" for jar in SparkConfig.REQUIRED_JARS]
    builder = builder.config("spark.jars", ",".join(jar_paths))
    
    spark = builder.getOrCreate()
    
    print(f"Created custom Spark session: {app_name}")
    return spark


if __name__ == "__main__":
    # Example usage
    spark = create_production_spark_session("MyProductionApp")
    
    # Example with custom configurations
    custom_configs = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true"
    }
    
    custom_spark = create_custom_spark_session("MyCustomApp", custom_configs)
    
    # Clean up
    spark.stop()
    custom_spark.stop()