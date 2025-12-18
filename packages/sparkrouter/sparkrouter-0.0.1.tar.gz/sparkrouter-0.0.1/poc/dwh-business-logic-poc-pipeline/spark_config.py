"""
Centralized Spark configuration for consistent setup across environments.

This module provides standardized Spark configurations that ensure:
- Docker environment matches integration tests
- Integration tests match production
- All JAR dependencies are consistently managed
- Configuration drift is eliminated
"""

import os
from typing import Dict, List
from pyspark.sql import SparkSession


class SparkConfig:
    """Centralized Spark configuration management"""
    
    # Core Spark configurations used across all environments
    BASE_CONFIG = {
        "spark.sql.shuffle.partitions": "1",
        "spark.ui.enabled": "false", 
        "spark.python.worker.reuse": "false",
        "spark.driver.host": "localhost",
        "spark.sql.debug.maxToStringFields": "500",
        # Logging configuration to reduce noise and highlight errors
        "spark.driver.extraJavaOptions": "-Dlog4j2.configurationFile=/opt/bitnami/spark/conf/log4j2.properties -Dlog4j.logger.org.apache.spark.SparkContext=ERROR",
        "spark.executor.extraJavaOptions": "-Dlog4j2.configurationFile=/opt/bitnami/spark/conf/log4j2.properties -Dlog4j.logger.org.apache.spark.SparkContext=ERROR",
        # Delta Lake configurations
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        # S3/MinIO configurations for Docker environment
        "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
        "spark.hadoop.fs.s3a.access.key": "minioadmin", 
        "spark.hadoop.fs.s3a.secret.key": "minioadmin",
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.permissions.umask-mode": "000",
        "spark.hadoop.fs.permissions.enabled": "false"
    }
    
    # Required JAR dependencies
    REQUIRED_JARS = [
        "postgresql-42.6.0.jar",  # PostgreSQL JDBC
        "delta-spark_2.12-3.0.0.jar",  # Delta Lake core
        "delta-storage-3.0.0.jar",  # Delta Lake storage
        "decryption-udfs_2.12-1.0.0.jar",
        "platform.infrastructure-1.19.5-SNAPSHOT.jar"
    ]
    
    @classmethod
    def get_docker_submit_options(cls) -> str:
        """Get Spark submit options for Docker environment"""
        config_pairs = [f"--conf {key}={value}" for key, value in cls.BASE_CONFIG.items()]
        return " ".join(config_pairs)
    
    @classmethod
    def get_session_builder(cls, app_name: str, master: str = "local[1]") -> SparkSession.Builder:
        """Get configured SparkSession builder"""
        builder = SparkSession.builder.appName(app_name).master(master)
        
        # Apply all base configurations
        for key, value in cls.BASE_CONFIG.items():
            builder = builder.config(key, value)
            
        return builder
    
    @classmethod
    def create_test_session(cls, additional_jar_paths: List[str] = None) -> SparkSession:
        """Create Spark session for integration tests with JAR downloading"""
        import sys
        import tempfile
        import urllib.request
        
        # Set Python paths for Spark
        python_path = sys.executable
        os.environ["PYSPARK_PYTHON"] = python_path
        os.environ["PYSPARK_DRIVER_PYTHON"] = python_path
        
        # Download required JARs to business-logic/jars directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        jar_dir = os.path.join(project_root, "jars")
        os.makedirs(jar_dir, exist_ok=True)
        
        jar_paths = additional_jar_paths or []
        
        # SQLite JDBC driver for tests
        sqlite_jar_url = "https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.42.0.0/sqlite-jdbc-3.42.0.0.jar"
        sqlite_jar_path = os.path.join(jar_dir, "sqlite-jdbc-3.42.0.0.jar")
        if not os.path.exists(sqlite_jar_path):
            print(f"Downloading SQLite JDBC driver to {sqlite_jar_path}")
            urllib.request.urlretrieve(sqlite_jar_url, sqlite_jar_path)
        jar_paths.append(sqlite_jar_path)
        
        # Delta Lake JARs
        delta_core_jar_url = "https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.0.0/delta-spark_2.12-3.0.0.jar"
        delta_storage_jar_url = "https://repo1.maven.org/maven2/io/delta/delta-storage/3.0.0/delta-storage-3.0.0.jar"
        
        delta_core_jar_path = os.path.join(jar_dir, "delta-spark_2.12-3.0.0.jar")
        delta_storage_jar_path = os.path.join(jar_dir, "delta-storage-3.0.0.jar")
        
        if not os.path.exists(delta_core_jar_path):
            print(f"Downloading Delta Core JAR to {delta_core_jar_path}")
            urllib.request.urlretrieve(delta_core_jar_url, delta_core_jar_path)
        jar_paths.append(delta_core_jar_path)
        
        if not os.path.exists(delta_storage_jar_path):
            print(f"Downloading Delta Storage JAR to {delta_storage_jar_path}")
            urllib.request.urlretrieve(delta_storage_jar_url, delta_storage_jar_path)
        jar_paths.append(delta_storage_jar_path)
        
        builder = cls.get_session_builder("DataSourceIntegrationTests")
        builder = builder.config("spark.jars", ",".join(jar_paths))
            
        return builder.getOrCreate()
    
    @classmethod
    def create_production_session(cls, app_name: str, jar_dir: str = "/opt/spark/jars") -> SparkSession:
        """Create Spark session for production environment"""
        # Build JAR paths for production
        jar_paths = [os.path.join(jar_dir, jar) for jar in cls.REQUIRED_JARS]
        
        builder = cls.get_session_builder(app_name, "yarn")
        builder = builder.config("spark.jars", ",".join(jar_paths))
        
        return builder.getOrCreate()
    
    @classmethod
    def get_docker_compose_config(cls) -> Dict[str, str]:
        """Get environment variables for docker-compose"""
        return {
            "SPARK_SUBMIT_OPTIONS": cls.get_docker_submit_options()
        }