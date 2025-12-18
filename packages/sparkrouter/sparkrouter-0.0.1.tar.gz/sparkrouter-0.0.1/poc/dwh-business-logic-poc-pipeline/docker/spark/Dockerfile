FROM bitnami/spark:3.5.1

USER root

# Install curl and download required JARs
RUN apt-get update && apt-get install -y curl && \
    curl --insecure -o /opt/bitnami/spark/jars/postgresql-42.6.0.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar && \
    curl --insecure -o /opt/bitnami/spark/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl --insecure -o /opt/bitnami/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl --insecure -o /opt/bitnami/spark/jars/delta-spark_2.12-3.0.0.jar \
    https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.0.0/delta-spark_2.12-3.0.0.jar && \
    curl --insecure -o /opt/bitnami/spark/jars/delta-storage-3.0.0.jar \
    https://repo1.maven.org/maven2/io/delta/delta-storage/3.0.0/delta-storage-3.0.0.jar && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# If you install Python packages here, use trusted-host flags:
# Example:
# RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org boto3
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /tmp/requirements.txt

USER 1001