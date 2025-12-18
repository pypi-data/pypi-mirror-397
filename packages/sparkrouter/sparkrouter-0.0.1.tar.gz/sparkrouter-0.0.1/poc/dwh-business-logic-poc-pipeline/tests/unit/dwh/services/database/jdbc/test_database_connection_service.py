import pytest
from dwh.services.database.jdbc.jdbc_connection_service import (
    JdbcConnectionService,
    DirectJdbcService,
    SparkJdbcService
)
from unit.noops import NoopSparkSession


def test_database_connection_service_abstract():
    """Test that JdbcConnectionService is abstract and can't be instantiated"""
    with pytest.raises(TypeError):
        JdbcConnectionService()


def test_direct_jdbc_service_init():
    """Test initialization of DirectJdbcService"""
    connection_details = {
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass'
    }
    
    svc = DirectJdbcService('POSTGRES', connection_details)
    assert svc.database_type == 'POSTGRES'
    assert svc.connection_details == connection_details
    assert svc.connection is None


def test_direct_jdbc_service_connect_unsupported():
    """Test connecting with unsupported database type"""
    svc = DirectJdbcService('UNSUPPORTED', {})
    with pytest.raises(ValueError, match="Unsupported database type"):
        svc.connect()


def test_direct_jdbc_service_sqlite():
    """Test SQLite connection configuration"""
    connection_details = {
        'database_path': ':memory:'
    }
    
    svc = DirectJdbcService('SQLITE', connection_details)
    assert svc.database_type == 'SQLITE'
    assert svc.connection_details['database_path'] == ':memory:'


def test_direct_jdbc_service_jdbc_url():
    """Test using JDBC URL in connection details"""
    connection_details = {
        'jdbc_url': 'jdbc:postgresql://localhost:5432/testdb',
        'user': 'testuser',
        'password': 'testpass'
    }
    
    svc = DirectJdbcService('POSTGRES', connection_details)
    assert svc.database_type == 'POSTGRES'
    assert svc.connection_details['jdbc_url'] == 'jdbc:postgresql://localhost:5432/testdb'


def test_spark_jdbc_service_init():
    """Test initialization of SparkJdbcService"""
    spark = NoopSparkSession()
    connection_details = {
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass'
    }
    
    svc = SparkJdbcService('POSTGRES', connection_details, spark)
    assert svc.database_type == 'POSTGRES'
    assert svc.connection_details == connection_details
    assert svc.spark == spark
    assert svc.jdbc_url == 'jdbc:postgresql://localhost:5432/testdb'


def test_spark_jdbc_service_connect():
    """Test SparkJdbcService connect method"""
    spark = NoopSparkSession()
    connection_details = {
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass'
    }
    
    svc = SparkJdbcService('POSTGRES', connection_details, spark)
    connection_info = svc.connect()
    
    assert connection_info['jdbc_url'] == 'jdbc:postgresql://localhost:5432/testdb'
    assert connection_info['user'] == 'testuser'
    assert connection_info['password'] == 'testpass'


def test_spark_jdbc_service_jdbc_url():
    """Test SparkJdbcService with JDBC URL"""
    spark = NoopSparkSession()
    connection_details = {
        'jdbc_url': 'jdbc:postgresql://custom-host:5555/customdb',
        'user': 'testuser',
        'password': 'testpass'
    }
    
    svc = SparkJdbcService('POSTGRES', connection_details, spark)
    assert svc.jdbc_url == 'jdbc:postgresql://custom-host:5555/customdb'


def test_spark_jdbc_service_unsupported_db_type():
    """Test that unsupported database types raise an error with Spark"""
    spark = NoopSparkSession()
    connection_details = {
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb'
    }
    
    with pytest.raises(ValueError, match="Unsupported database type for Spark JDBC"):
        SparkJdbcService('UNSUPPORTED', connection_details, spark)


def test_spark_jdbc_service_close():
    """Test SparkJdbcService close method (no-op)"""
    spark = NoopSparkSession()
    connection_details = {
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb'
    }
    
    svc = SparkJdbcService('POSTGRES', connection_details, spark)
    # This should not raise any exceptions
    svc.close()