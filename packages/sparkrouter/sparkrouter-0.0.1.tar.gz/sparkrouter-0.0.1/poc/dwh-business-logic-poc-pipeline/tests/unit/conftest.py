import pytest
from unit.noops import NoopSparkSession


@pytest.fixture(scope="session")
def unit_spark_session():
    """
    Noop Spark session for unit tests - no real Spark needed
    """
    return NoopSparkSession()


@pytest.fixture(scope="session")
def spark_session(unit_spark_session):
    """
    Alias for unit_spark_session to maintain compatibility
    """
    return unit_spark_session