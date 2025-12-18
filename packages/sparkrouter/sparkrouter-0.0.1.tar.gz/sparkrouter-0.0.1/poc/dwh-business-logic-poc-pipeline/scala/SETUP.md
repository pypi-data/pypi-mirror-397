# Scala UDF Setup Guide

This guide walks you through setting up a Scala UDF module within your Python project for high-performance decryption in Spark.

## Directory Structure

```
your-python-project/
├── src/
│   └── dwh/
│       └── jobs/
│           └── transform_images/
│               └── transform/
│                   └── image_transformer.py  (simplified, calls Scala UDF)
├── scala/                               (NEW - Scala module)
│   ├── build.sbt
│   ├── project/
│   │   └── build.properties
│   └── src/
│       └── main/
│           └── scala/
│               └── com/
│                   └── yourcompany/
│                       └── udfs/
│                           └── DecryptionUDFs.scala
├── jars/                                     (compiled JARs go here)
│   └── platform.infrastructure-1.19.5-SNAPSHOT.jar
└── ...
```

## Step 1: Install Prerequisites (WSL/Ubuntu)

### Install Java JDK 8 or 11
```bash
# Check if Java is installed
java -version

# If not installed:
sudo apt update
sudo apt install openjdk-11-jdk

# Verify
java -version
javac -version
```

### Install sbt (Scala Build Tool)
```bash
# Add sbt repository
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | sudo tee /etc/apt/sources.list.d/sbt_old.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add

# Install sbt
sudo apt update
sudo apt install sbt

# Verify
sbt --version
```

### Alternative: Install sbt via SDKMAN (recommended)
```bash
# Install SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Install sbt
sdk install sbt

# Verify
sbt --version
```

## Step 2: Create the Scala Module

Run these commands from your project root:

```bash
# Create directory structure
mkdir -p scala/src/main/scala/com/yourcompany/udfs
mkdir -p scala/project

# Copy the provided files (see below)
```

## Step 3: Build the JAR

```bash
cd scala

# First build (downloads dependencies, takes a few minutes)
sbt package

# Output JAR location:
# scala/target/scala-2.12/decryption-udfs_2.12-1.0.0.jar
```

## Step 4: Copy JAR to jars/ directory

```bash
# From project root
cp scala/target/scala-2.12/decryption-udfs_2.12-1.0.0.jar jars/
```

## Step 5: Configure Spark to Load the JARs

### Local Development / Tests
```python
spark = SparkSession.builder \
    .appName("ImageTransform") \
    .config("spark.jars", "jars/decryption-udfs_2.12-1.0.0.jar,jars/platform.infrastructure-1.19.5-SNAPSHOT.jar") \
    .getOrCreate()
```

### AWS Glue
Upload JARs to S3 and reference in job config:
```python
# In Glue job parameters
"--extra-jars": "s3://your-bucket/jars/decryption-udfs_2.12-1.0.0.jar,s3://your-bucket/jars/platform.infrastructure-1.19.5-SNAPSHOT.jar"
```

### Databricks
Upload JARs to DBFS or Unity Catalog, then:
```python
spark.conf.set("spark.jars", "dbfs:/path/to/decryption-udfs_2.12-1.0.0.jar,dbfs:/path/to/platform.infrastructure-1.19.5-SNAPSHOT.jar")
```

## Step 6: Register and Use the UDF in Python

```python
from pyspark.sql.types import StringType
from pyspark.sql.functions import expr, col

# Register the Scala UDF
spark.udf.registerJavaFunction(
    "decrypt_value",
    "com.shutterfly.dwh.udfs.DecryptionUDFs.decrypt",
    StringType()
)

# Use it
df.withColumn("decrypted", expr("decrypt_value(encrypted_column)"))
```

## Troubleshooting

### "class not found" error
- Ensure JAR is in spark.jars config
- Check package name matches exactly
- Verify JAR contains the class: `jar -tf your.jar | grep DecryptionUDFs`

### "method not found" error  
- Scala UDF methods must be in an `object`, not a `class`
- Method must take/return Java-compatible types (String, not Option[String])

### sbt download is slow
```bash
# Use a mirror (add to ~/.sbt/repositories)
[repositories]
local
maven-central: https://repo1.maven.org/maven2/
```

### Version mismatches
- Spark 3.x requires Scala 2.12
- Spark 2.x requires Scala 2.11
- Check your Spark version: `spark.version`
