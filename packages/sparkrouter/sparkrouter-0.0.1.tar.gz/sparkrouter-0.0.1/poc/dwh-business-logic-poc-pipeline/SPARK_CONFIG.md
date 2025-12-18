# Centralized Spark Configuration

This project uses centralized Spark configuration to ensure consistency across Docker, integration tests, and production environments.

## Overview

The `SparkConfig` class in `src/dwh/utils/spark_config.py` provides:
- Standardized Spark configurations
- Consistent JAR dependency management
- Environment-specific session creation
- Elimination of configuration drift

## Usage

### Integration Tests
Tests automatically use centralized configuration via the `spark_session` fixture:

```python
def test_my_feature(spark_session):
    # spark_session uses SparkConfig.create_test_session()
    df = spark_session.createDataFrame(data)
```

### Production
Use `SparkConfig` to create production sessions:

```python
from dwh.utils.spark_config import SparkConfig

# Standard production session
spark = SparkConfig.create_production_session("MyApp")

# Custom session with additional configs
builder = SparkConfig.get_session_builder("MyApp", "yarn")
builder = builder.config("spark.sql.adaptive.enabled", "true")
spark = builder.getOrCreate()
```

### Docker Environment
Generate Docker configuration from centralized config:

```bash
python scripts/generate_docker_config.py
```

Copy the output to your `docker-compose.yml` `SPARK_SUBMIT_OPTIONS`.

## Configuration Details

### Base Configuration
All environments use these core settings:
- Delta Lake extensions enabled
- Optimized for data processing workloads
- S3/MinIO connectivity configured
- Consistent partitioning and performance settings

### Required JARs
- `postgresql-42.6.0.jar` - PostgreSQL JDBC driver
- `delta-spark_2.12-3.0.0.jar` - Delta Lake core
- `delta-storage-3.0.0.jar` - Delta Lake storage

### Environment Differences
- **Tests**: `local[1]` master, downloaded JARs
- **Docker**: Cluster mode, mounted JARs
- **Production**: `yarn` master, system JARs

## Benefits

1. **Consistency**: Same configuration across all environments
2. **Maintainability**: Single source of truth for Spark settings
3. **Reliability**: Eliminates environment-specific configuration bugs
4. **Scalability**: Easy to add new configurations or environments

## Adding New Configurations

1. Update `SparkConfig.BASE_CONFIG` for settings used everywhere
2. Add environment-specific logic in the appropriate `create_*_session` method
3. Update `REQUIRED_JARS` if new dependencies are needed
4. Regenerate Docker configuration with the script

## Troubleshooting

If you encounter Spark configuration issues:

1. Verify all environments use `SparkConfig`
2. Check JAR availability in each environment
3. Compare actual vs expected configurations using Spark UI
4. Ensure Docker configuration matches generated output