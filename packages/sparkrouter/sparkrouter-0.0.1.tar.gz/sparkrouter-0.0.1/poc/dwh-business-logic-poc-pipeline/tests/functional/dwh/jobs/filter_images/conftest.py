# Python
# File: 'tests/functional/dwh/jobs/filter_images/conftest.py'
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="function")
def spark_session():
    """
    Spark session for filter_images functional tests.

    Uses local[*] mode. No special JARs required since filter_images
    operates on already-transformed data (parquet files).
    """
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("filter-images-test")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )

    yield spark
    spark.stop()
