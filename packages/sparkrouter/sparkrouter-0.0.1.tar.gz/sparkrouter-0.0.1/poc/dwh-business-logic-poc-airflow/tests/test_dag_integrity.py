from airflow.models import DagBag
import os

def test_dag_integrity():
    """Test there are no DAG import errors"""
    # Get the directory where DAG files are stored
    dag_path = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(dag_path)
    dags_dir = os.path.join(parent_dir, "src")

    # Load the DAG bag which processes all DAGs in the specified folder
    dag_bag = DagBag(dag_folder=dags_dir, include_examples=False)

    # Assert there are no import errors
    assert not dag_bag.import_errors, f"DAG import errors: {dag_bag.import_errors}"

    # Optional: Ensure at least one DAG was found
    assert len(dag_bag.dags) > 0, "No DAGs found in the specified directory"

    # Print found DAGs for debugging purposes
    print(f"Successfully loaded {len(dag_bag.dags)} DAGs:")
    for dag_id in dag_bag.dags:
        print(f"  - {dag_id}")