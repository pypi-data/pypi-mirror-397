#!/bin/bash
# Wrapper script to run spark-submit with generic_entry.py

# Install required packages
echo "Installing required Python packages..."
pip install -r /opt/bitnami/spark/work/spark/requirements.txt

# Verify psycopg2 installation
echo "Verifying psycopg2 installation:"
pip list | grep psycopg2

echo "=== Spark Version Check ==="
/opt/bitnami/spark/bin/spark-submit --version 2>&1 || echo "Version command failed"
echo "=== End Version Check ==="

# Also check what's actually in the Spark directory
echo "=== Spark Installation Check ==="
ls -la /opt/bitnami/spark/bin/
echo "=== Spark JARs Check ==="
ls -la /opt/bitnami/spark/jars/ | grep -E "(spark-core|delta)" | head -5
echo "=========================="

# Run spark-submit with generic_entry.py
/opt/bitnami/spark/bin/spark-submit \
  --conf "spark.executorEnv.PYTHONPATH=/opt/bitnami/spark/src" \
  --conf "spark.driver.extraJavaOptions=-Dpython.path=/opt/bitnami/spark/src -Dlog4j2.configurationFile=/opt/bitnami/spark/work/spark/log4j2.properties" \
  --conf "spark.executor.extraJavaOptions=-Dlog4j2.configurationFile=/opt/bitnami/spark/work/spark/log4j2.properties" \
  --conf "spark.hadoop.fs.s3a.endpoint=http://minio:9000" \
  --conf "spark.hadoop.fs.s3a.access.key=minioadmin" \
  --conf "spark.hadoop.fs.s3a.secret.key=minioadmin" \
  --conf "spark.hadoop.fs.s3a.path.style.access=true" \
  --conf "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem" \
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
  /opt/bitnami/spark/scripts/container/generic_entry.py "$@"