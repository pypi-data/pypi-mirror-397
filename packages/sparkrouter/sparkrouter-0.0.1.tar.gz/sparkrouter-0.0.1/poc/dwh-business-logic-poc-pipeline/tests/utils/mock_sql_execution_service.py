from typing import Any

from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService


class MockDatabaseConnectionService(JdbcConnectionService):
    """Mock implementation of DatabaseConnectionService for testing"""

    def __init__(self, results=None):
        self.results = results or [{'column1': 'value1', 'column2': 'value2'}]
        self.executed_queries = []
        self.executed_params = []

    def connect(self) -> Any:
        pass

    def execute_query(self, sql, params=None):
        self.executed_queries.append(sql)
        self.executed_params.append(params)
        return self.results

    def close(self):
        pass
