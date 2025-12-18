# Design Pattern: Connection-Agnostic Job Factory

## Design Pattern
1. Define a Common Interface

```python
class DatabaseConnector:
    def read(self, table_name: str):
        raise NotImplementedError

    def write(self, df, table_name: str):
        raise NotImplementedError
```

2. Implement Spark-Based Connector

```python
class SparkDatabaseConnector(DatabaseConnector):
    def __init__(self, spark_session, jdbc_url, props):
        self.spark = spark_session
        self.url = jdbc_url
        self.props = props

    def read(self, table_name):
        return self.spark.read.jdbc(self.url, table_name, properties=self.props)

    def write(self, df, table_name):
        df.write.jdbc(self.url, table_name, mode="overwrite", properties=self.props)
```

3. Implement Non-Spark Connector (e.g., Pandas + SQLAlchemy)

```python
import pandas as pd
from sqlalchemy import create_engine

class PandasDatabaseConnector(DatabaseConnector):
    def __init__(self, sqlalchemy_url):
        self.engine = create_engine(sqlalchemy_url)

    def read(self, table_name):
        return pd.read_sql_table(table_name, self.engine)

    def write(self, df, table_name):
        df.to_sql(table_name, self.engine, if_exists="replace", index=False)
```

4. Factory to Choose Connector

```python
def get_connector(mode: str, **kwargs) -> DatabaseConnector:
    if mode == "spark":
        return SparkDatabaseConnector(kwargs["spark"], kwargs["jdbc_url"], kwargs["props"])
    elif mode == "pandas":
        return PandasDatabaseConnector(kwargs["sqlalchemy_url"])
    else:
        raise ValueError("Unsupported mode")
```

## Why This Works

* Keeps your job logic agnostic to the execution engine.
* Makes testing easier—especially for your middle-tier logic tests.
* Enables you to plug in different backends (e.g., DuckDB, SQLite) for local dev or CI.