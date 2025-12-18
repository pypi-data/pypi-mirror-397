"""
Integration test configuration and fixtures
"""
import psycopg2
import pytest
import os
import subprocess
import time
from .job_runner import DockerSparkRunner
from .validators import FileResultValidator

# Database connection environment variables
ENV_PG_HOST = "TEST_PG_HOST"
ENV_PG_PORT = "TEST_PG_PORT"
ENV_PG_DB = "TEST_PG_DATABASE"
ENV_PG_USER = "TEST_PG_USERNAME"
ENV_PG_PASS = "TEST_PG_PASSWORD"


@pytest.fixture
def docker_spark_runner():
    """Fixture for Docker Spark job runner"""
    docker_dir = os.path.join(os.getcwd(), "docker")
    return DockerSparkRunner(docker_dir)


@pytest.fixture
def file_validator():
    """Fixture for file result validator"""
    spark_data_dir = os.path.join(os.getcwd(), "docker", "spark-data")
    return FileResultValidator(spark_data_dir)


@pytest.fixture
def test_data_cleanup():
    """Fixture to clean up test data after tests"""
    cleanup_tasks = []

    def add_cleanup(task):
        cleanup_tasks.append(task)

    yield add_cleanup

    # Run cleanup tasks
    for task in cleanup_tasks:
        try:
            task()
        except Exception as e:
            print(f"Cleanup task failed: {e}")


@pytest.fixture(scope="session", autouse=True)
def ensure_docker_running():
    """Ensure Docker services are running before tests"""
    docker_dir = os.path.join(os.getcwd(), "docker")

    # Check if Docker is running
    try:
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.fail("Docker is not running. Please start Docker first.")

    # Check if containers are running
    result = subprocess.run(
        ["docker-compose", "-f", "docker-compose.yml", "ps", "-q", "spark"],
        cwd=docker_dir,
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        print("Starting Docker services...")
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.yml", "up", "-d"],
            cwd=docker_dir,
            check=True
        )

        # Wait for services to be ready
        print("Waiting for services to be ready...")
        time.sleep(10)

    # Yield to allow tests to run
    yield

    # Don't stop containers after tests to allow for faster subsequent test runs
    # Users can manually stop with docker-compose down if needed



@pytest.fixture
def s3_client():
    """Fixture for MinIO S3 client"""
    import boto3
    from botocore.config import Config

    return boto3.client(
        's3',
        endpoint_url="http://localhost:9002",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )


def get_postgres_params():
    """Get PostgreSQL connection parameters from environment variables."""
    return {
        "host": os.environ.get(ENV_PG_HOST, "localhost"),
        "port": int(os.environ.get(ENV_PG_PORT, "5432")),
        "database": os.environ.get(ENV_PG_DB, "postgres_db"),
        "username": os.environ.get(ENV_PG_USER, "postgres_user"),
        "password": os.environ.get(ENV_PG_PASS, "postgres_password"),
        "ssl_mode": "prefer"
    }


def get_postgres_conn():
    return psycopg2.connect(
        host=os.environ.get(ENV_PG_HOST, "localhost"),  # or "postgres" if running inside Docker network
        port=int(os.environ.get(ENV_PG_PORT, "5432")),
        dbname=os.environ.get(ENV_PG_DB, "postgres_db"),
        user=os.environ.get(ENV_PG_USER, "postgres_user"),
        password=os.environ.get(ENV_PG_PASS, "postgres_password"),
    )


def get_redshift_params():
    """Get Redshift connection parameters from environment variables."""
    return {
        "host": os.environ.get(ENV_PG_HOST, "localhost"),
        "port": int(os.environ.get(ENV_PG_PORT, "5439")),
        "database": os.environ.get(ENV_PG_DB, "redshift_db"),
        "username": os.environ.get(ENV_PG_USER, "redshift_user"),
        "password": os.environ.get(ENV_PG_PASS, "redshift_password"),
        "ssl_mode": "prefer"
    }


@pytest.fixture
def clean_database():
    """Fixture to ensure clean database state for integration tests.
    
    This fixture:
    1. Drops all non-system schemas to ensure clean state before test
    2. Provides a database connection for the test
    3. Cleans up after test completion
    
    Each test is responsible for creating the schemas/tables it needs.
    """
    conn = get_postgres_conn()
    
    try:
        # Import here to avoid circular imports
        from .utils.sql_utils import SQLUtils
        
        # Clean up any existing schemas before test
        SQLUtils.drop_all_non_system_schemas(conn)
        
        yield conn
        
    finally:
        # Cleanup after test
        try:
            SQLUtils.drop_all_non_system_schemas(conn)
        except Exception as e:
            print(f"Cleanup failed: {e}")
        finally:
            conn.close()
