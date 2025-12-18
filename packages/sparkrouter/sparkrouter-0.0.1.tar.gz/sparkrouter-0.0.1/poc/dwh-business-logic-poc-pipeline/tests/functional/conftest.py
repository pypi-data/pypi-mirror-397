import pytest
import tempfile
import os
import urllib.request
from spark_config import SparkConfig


@pytest.fixture(scope="function")
def functional_spark_session():
    """
    Spark session for functional tests with full JAR dependencies
    """
    spark = None
    try:
        spark = SparkConfig.create_test_session()
        yield spark
    finally:
        if spark:
            try:
                spark.stop()
            except Exception as e:
                print(f"Warning: Error stopping Spark session: {e}")


@pytest.fixture(scope="function")
def spark_session(functional_spark_session):
    """
    Alias for functional_spark_session to maintain compatibility
    """
    return functional_spark_session