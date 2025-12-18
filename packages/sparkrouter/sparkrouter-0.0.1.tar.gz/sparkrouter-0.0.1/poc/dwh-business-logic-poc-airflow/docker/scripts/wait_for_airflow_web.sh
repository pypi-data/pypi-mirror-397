#!/bin/bash
set -e

# Configuration
MAX_RETRIES=60
RETRY_INTERVAL=5
AIRFLOW_HOST="airflow-web"
AIRFLOW_PORT="8080"
HEALTH_ENDPOINT="/health"

echo "Waiting for Airflow web server to be ready..."

# Try to connect to the Airflow web server
retries=0
while [ $retries -lt $MAX_RETRIES ]; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://${AIRFLOW_HOST}:${AIRFLOW_PORT}${HEALTH_ENDPOINT} || echo "000")

    if [ "$status_code" == "200" ]; then
        echo "Airflow web server is ready!"
        exit 0
    fi

    echo "Airflow web server not ready yet (status code: $status_code). Retrying in ${RETRY_INTERVAL} seconds..."
    sleep $RETRY_INTERVAL
    retries=$((retries+1))
done

echo "Error: Timed out waiting for Airflow web server after $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
exit 1