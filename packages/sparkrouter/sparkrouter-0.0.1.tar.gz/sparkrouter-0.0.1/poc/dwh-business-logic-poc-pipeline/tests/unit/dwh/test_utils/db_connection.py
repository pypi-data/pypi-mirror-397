class MockDBConnection:
    """A simple mock database connection for testing"""

    def __init__(self, expected_results=None):
        self.expected_results = expected_results or []
        self.executed_queries = []
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return MockCursor(self.expected_results)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class MockCursor:
    """A simple mock database cursor for testing"""

    def __init__(self, expected_results):
        self.expected_results = expected_results
        self.executed_queries = []
        self.description = [('column1',), ('column2',)] if expected_results else None
        self.closed = False

    def execute(self, query):
        self.executed_queries.append(query)
        return len(self.expected_results)

    def fetchall(self):
        return [list(row.values()) for row in self.expected_results]

    def close(self):
        self.closed = True
