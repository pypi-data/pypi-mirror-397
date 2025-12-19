# Airflow DAG Examples

Minimal examples for running SparkRouter jobs via Airflow.

## Files

| File | Platform |
|------|----------|
| `dag_glue.py` | AWS Glue |
| `dag_databricks.py` | Databricks |

## Prerequisites

See the main [README](../../README.md#platform-deployment) for entry script setup.

## Required Airflow Providers

```bash
pip install apache-airflow-providers-amazon      # For Glue
pip install apache-airflow-providers-databricks  # For Databricks
```
