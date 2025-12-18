from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class JdbcConnectionService(ABC):
    """Abstract base class for database connection services."""

    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database"""
        pass

    @abstractmethod
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection"""
        pass


class DirectJdbcService(JdbcConnectionService):
    """Direct JDBC connection service."""

    def __init__(self, database_type: str, connection_details: Dict[str, Any]):
        self.database_type = database_type
        self.connection_details = connection_details
        self.connection = None

    def connect(self) -> Any:
        """Establish a direct database connection."""
        if self.connection is not None:
            return self.connection

        if self.database_type == 'POSTGRES' or self.database_type == 'REDSHIFT':
            self._connect_postgres()
        elif self.database_type == 'MYSQL':
            self._connect_mysql()
        elif self.database_type == 'ORACLE':
            self._connect_oracle()
        elif self.database_type == 'SQLITE':
            self._connect_sqlite()
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")

        return self.connection

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        if self.connection is None:
            self.connect()

        # Use named parameter SQL template
        from dwh.utils.sql.named_parameter_sql import NamedParameterSQLTemplate
        template = NamedParameterSQLTemplate(sql)
        return template.execute_query(self.connection, params or {})

    def close(self) -> None:
        """Close the database connection."""
        if self.connection and hasattr(self.connection, 'close'):
            self.connection.close()
        self.connection = None

    def _connect_postgres(self) -> None:
        """Connect to PostgreSQL or Redshift database."""
        import psycopg2

        # Use JDBC URL if available
        if 'jdbc_url' in self.connection_details:
            import re
            jdbc_url = self.connection_details['jdbc_url']
            match = re.match(r'jdbc:(postgresql|redshift)://([^:/]+):(\d+)/(\w+)', jdbc_url)
            if match:
                host = match.group(2)
                port = int(match.group(3))
                database = match.group(4)
            else:
                raise ValueError(f"Invalid JDBC URL: {jdbc_url}")
        else:
            host = self.connection_details['host']
            port = int(self.connection_details['port'])
            database = self.connection_details['database']

        self.connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=self.connection_details.get('user', ''),
            password=self.connection_details.get('password', '')
        )

    def _connect_mysql(self) -> None:
        """Connect to MySQL database."""
        # import mysql.connector
        # Implementation similar to _connect_postgres
        # ...

    def _connect_oracle(self) -> None:
        """Connect to Oracle database."""
        # import oracledb
        # Implementation similar to _connect_postgres
        # ...

    def _connect_sqlite(self) -> None:
        """Connect to SQLite database."""
        import sqlite3

        if 'jdbc_url' in self.connection_details:
            path = self.connection_details['jdbc_url'].replace('jdbc:sqlite:', '')
        else:
            path = self.connection_details.get('database_path', ':memory:')

        self.connection = sqlite3.connect(path)


class SparkJdbcService(JdbcConnectionService):
    """Spark-based JDBC connection service."""

    def __init__(self, database_type: str, connection_details: Dict[str, Any], spark_session):
        self.database_type = database_type
        self.connection_details = connection_details
        self.spark = spark_session
        self.jdbc_url = self._build_jdbc_url()

    def connect(self) -> Any:
        """No actual connection needed for Spark, just return connection info."""
        return {
            'jdbc_url': self.jdbc_url,
            'user': self.connection_details.get('user'),
            'password': self.connection_details.get('password')
        }

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query using Spark JDBC and return results."""
        # Replace parameters in SQL
        from dwh.utils.sql.named_parameter_sql import NamedParameterSQLTemplate
        template = NamedParameterSQLTemplate(sql)
        formatted_sql = template.format(params or {})

        # Read from database using Spark JDBC
        df = self.spark.read \
            .format("jdbc") \
            .option("url", self.jdbc_url) \
            .option("dbtable", f"({formatted_sql}) AS query") \
            .option("user", self.connection_details.get('user')) \
            .option("password", self.connection_details.get('password')) \
            .load()

        # Convert Spark DataFrame to list of dictionaries
        return [row.asDict() for row in df.collect()]

    def close(self) -> None:
        """No need to close Spark connections."""
        pass

    def _build_jdbc_url(self) -> str:
        """Build or get JDBC URL."""
        # Use provided JDBC URL if available
        if 'jdbc_url' in self.connection_details:
            return self.connection_details['jdbc_url']

        # Otherwise build from components
        host = self.connection_details['host']
        port = self.connection_details['port']
        database = self.connection_details['database']

        if self.database_type == 'POSTGRES':
            return f"jdbc:postgresql://{host}:{port}/{database}"
        elif self.database_type == 'MYSQL':
            return f"jdbc:mysql://{host}:{port}/{database}"
        elif self.database_type == 'ORACLE':
            return f"jdbc:oracle:thin:@{host}:{port}:{database}"
        elif self.database_type == 'REDSHIFT':
            return f"jdbc:redshift://{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type for Spark JDBC: {self.database_type}")
