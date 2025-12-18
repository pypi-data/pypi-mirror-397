# Quick Reference: Scala UDF Build & Deploy

## One-Time Setup (WSL/Ubuntu)

```bash
# Install Java (if needed)
sudo apt install openjdk-11-jdk

# Install sbt
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install sbt
```

## Build the JAR

```bash
cd scala
sbt package
cp target/scala-2.12/decryption-udfs_2.12-1.0.0.jar ../jars/
```

## Use in Python

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

# Create session with JARs
spark = SparkSession.builder \
    .config("spark.jars", "jars/decryption-udfs_2.12-1.0.0.jar,jars/platform.infrastructure-1.19.5-SNAPSHOT.jar") \
    .getOrCreate()

# Register UDFs
from pyspark.sql.types import StringType, StructType, StructField

# Simple decrypt
spark.udf.registerJavaFunction("decrypt_value", "com.shutterfly.dwh.udfs.DecryptUDF", StringType())

# Combined decrypt + parse (returns struct)
schema = StructType([
    StructField("msp", StringType(), True),
    StructField("mspid", StringType(), True),
    StructField("mediaid", StringType(), True),
    StructField("locationspec", StringType(), True)
])
spark.udf.registerJavaFunction("decrypt_and_parse", "com.shutterfly.dwh.udfs.DecryptAndParseUDF", schema)

# Use it
df.withColumn("result", expr("decrypt_and_parse(image_view, image_id, image_data)"))
```

## Deploy to AWS Glue

```bash
# Upload JARs to S3
aws s3 cp jars/decryption-udfs_2.12-1.0.0.jar s3://your-bucket/jars/
aws s3 cp jars/platform.infrastructure-1.19.5-SNAPSHOT.jar s3://your-bucket/jars/
```

In Glue job config:
```
--extra-jars: s3://your-bucket/jars/decryption-udfs_2.12-1.0.0.jar,s3://your-bucket/jars/platform.infrastructure-1.19.5-SNAPSHOT.jar
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| Class not found | Check spark.jars path |
| Method not found | Ensure using object not class |
| Serialization error | Check Spark/Scala version match |

## Performance Comparison

| Approach | 10M unique values |
|----------|-------------------|
| Broadcast (Python) | ~2.7 hours (sequential on driver) |
| Scala UDF | Minutes (parallel on executors) |
