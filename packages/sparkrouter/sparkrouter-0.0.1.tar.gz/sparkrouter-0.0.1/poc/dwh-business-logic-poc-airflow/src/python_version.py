"""
DAG which displays current python version and list of installed packages to the log
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import sys


def print_python_version():
    print(f"Python version: {sys.version}")

    # Method 1: Using pip list
    result = subprocess.check_output([sys.executable, '-m', 'pip', 'list']).decode('utf-8')
    print("Installed packages:")
    print(result)

    return sys.version


with DAG('check_python_version',
         start_date=datetime(2023, 1, 1),
         schedule=None) as dag:

    task = PythonOperator(
        task_id='python_version_check',
        python_callable=print_python_version
    )
