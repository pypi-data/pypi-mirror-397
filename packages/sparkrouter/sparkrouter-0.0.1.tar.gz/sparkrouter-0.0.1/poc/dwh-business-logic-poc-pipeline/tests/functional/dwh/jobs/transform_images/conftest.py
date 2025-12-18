# Python
# File: 'tests/functional/dwh/jobs/transform_images/conftest.py'
import pytest
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructType, StructField


def _register_decryption_udfs(spark: SparkSession) -> None:
    """
    Register Scala decryption UDFs with Spark.
    Must be called after SparkSession creation and JAR loading.
    """
    # Combined decrypt + parse UDF (returns struct)
    decrypt_schema = StructType([
        StructField("msp", StringType(), True),
        StructField("mspid", StringType(), True),
        StructField("mediaid", StringType(), True),
        StructField("locationspec", StringType(), True),
    ])

    spark.udf.registerJavaFunction(
        "decrypt_and_parse",
        "com.shutterfly.dwh.udfs.DecryptAndParseUDF",
        decrypt_schema
    )

    # Simple decrypt UDF (for ad-hoc use)
    spark.udf.registerJavaFunction(
        "decrypt_value",
        "com.shutterfly.dwh.udfs.DecryptUDF",
        StringType()
    )


@pytest.fixture(scope="function")
def spark_session():
    """
    Spark session with Scala decryption UDFs.

    Now uses local[*] mode since the Scala UDF runs natively in the JVM,
    eliminating the Python UDF JVM access issues that required local-cluster mode.

    JARs required:
    - decryption-udfs_2.12-1.0.0.jar: Scala UDFs for parallel decryption
    - platform.infrastructure-1.19.5-SNAPSHOT.jar: SecurityUtils dependency
    """
    # From tests/functional/dwh/jobs/transform_images/conftest.py -> project root (6 levels up)
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    jars_dir = project_root / "jars"

    required_jars = [
        "decryption-udfs_2.12-1.0.0.jar",
        "platform.infrastructure-1.19.5-SNAPSHOT.jar",
    ]

    # Verify JARs exist and build paths
    jar_paths = []
    for jar_name in required_jars:
        jar_path = jars_dir / jar_name
        if not jar_path.exists():
            raise FileNotFoundError(
                f"JAR not found: {jar_path}\n"
                f"Expected path: {jar_path.absolute()}\n"
                f"conftest.py location: {Path(__file__).absolute()}"
            )
        jar_paths.append(str(jar_path.absolute()))
        # jar_paths.append(str(jar_path))

    jar_paths_str = ",".join(jar_paths)
    # import sys
    # print(f"DEBUG: Python executable: {sys.executable}", file=sys.stderr)
    # print(f"DEBUG: Current working directory: {Path.cwd()}", file=sys.stderr)
    # print(f"DEBUG: JAR paths string: {jar_paths_str}", file=sys.stderr)
    # for jar in jar_paths:
    #     print(f"DEBUG: JAR exists? {Path(jar).exists()} - {jar}", file=sys.stderr)

    spark = (
        SparkSession.builder
        .master("local[*]")  # No need for local-cluster with Scala UDFs
        .appName("image-transform-test")
        .config("spark.jars", jar_paths_str)
        .config("spark.driver.extraClassPath", jar_paths_str)
        .config("spark.executor.extraClassPath", jar_paths_str)
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )

    # Register Scala UDFs - this is the critical step!
    _register_decryption_udfs(spark)

    yield spark
    spark.stop()


@pytest.fixture
def s3_stub():
    """
    Minimal S3 stub for functional tests.
    Allows injecting JSONL data paths and retrieving them later if needed.
    Extend as your job requires.
    """

    class S3Stub:
        def __init__(self):
            self._store = {}

        def add_jsonl_data(self, path, data):
            # Store raw records keyed by path
            self._store[path] = list(data)

        def get_jsonl_data(self, path):
            return self._store.get(path, [])

        def clear(self):
            self._store.clear()

    return S3Stub()