import pytest

from dwh.services.database.jdbc.jdbc_connection_service_factory import JdbcConnectionServiceFactory
from dwh.services.database.jdbc.jdbc_connection_service import DirectJdbcService, SparkJdbcService
from unit.noops import NoopSparkSession


def test_missing_database_type():
    """Test that missing database_type raises an error"""
    with pytest.raises(ValueError, match="database_type is required"):
        JdbcConnectionServiceFactory.create_connection({})


def test_invalid_db_type():
    """Test that invalid database_type raises an error when connecting"""
    # The factory itself doesn't validate database types, but the service does when connecting
    svc = JdbcConnectionServiceFactory.create_connection({
        'database_type': 'INVALID'
    })
    
    # The error happens when we try to connect
    with pytest.raises(ValueError, match="Unsupported database type"):
        svc.connect()


def test_sqlite_direct_params():
    """Test creating SQLite connection with direct parameters"""
    svc = JdbcConnectionServiceFactory.create_connection({
        'database_type': 'SQLITE',
        'database_path': '/path/to/sqlite.db'
    })
    assert isinstance(svc, DirectJdbcService)
    assert svc.database_type == 'SQLITE'
    assert svc.connection_details['database_path'] == '/path/to/sqlite.db'


def test_postgres_direct_params():
    """Test creating Postgres connection with direct parameters"""
    svc = JdbcConnectionServiceFactory.create_connection({
        'database_type': 'POSTGRES',
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass'
    })
    assert isinstance(svc, DirectJdbcService)
    assert svc.database_type == 'POSTGRES'
    assert svc.connection_details['host'] == 'localhost'
    assert svc.connection_details['port'] == 5432


def test_jdbc_url():
    """Test creating connection with JDBC URL"""
    svc = JdbcConnectionServiceFactory.create_connection({
        'database_type': 'MYSQL',
        'jdbc_url': 'jdbc:mysql://localhost:3306/testdb',
        'user': 'testuser',
        'password': 'testpass'
    })
    assert isinstance(svc, DirectJdbcService)
    assert svc.database_type == 'MYSQL'
    assert svc.connection_details['jdbc_url'] == 'jdbc:mysql://localhost:3306/testdb'


def test_spark_connection():
    """Test creating Spark connection"""
    # Create a no-op Spark session
    noop_spark = NoopSparkSession()
    
    svc = JdbcConnectionServiceFactory.create_connection({
        'database_type': 'POSTGRES',
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass'
    }, spark_session=noop_spark)
    
    assert isinstance(svc, SparkJdbcService)
    assert svc.database_type == 'POSTGRES'
    assert svc.jdbc_url == 'jdbc:postgresql://localhost:5432/testdb'


def test_force_direct_connection():
    """Test forcing direct connection even with Spark available"""
    # Create a no-op Spark session
    noop_spark = NoopSparkSession()
    
    svc = JdbcConnectionServiceFactory.create_connection({
        'database_type': 'POSTGRES',
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass',
        'force_direct_connection': True
    }, spark_session=noop_spark)
    
    # Should be DirectJdbcService despite Spark being available
    assert isinstance(svc, DirectJdbcService)
    assert svc.database_type == 'POSTGRES'