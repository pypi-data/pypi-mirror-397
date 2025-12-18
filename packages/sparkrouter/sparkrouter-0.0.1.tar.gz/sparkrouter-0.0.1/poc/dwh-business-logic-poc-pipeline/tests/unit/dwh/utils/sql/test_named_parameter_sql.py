import pytest

from dwh.utils.sql.named_parameter_sql import NamedParameterSQLTemplate


class MockCursor:
    """Test stub for database cursor"""

    def __init__(self):
        self.executed_queries = []
        self.description = None
        self.fetch_results = []
        self.close_called = False
        self.should_raise_exception = False
        self.exception_message = ""

    def execute(self, query):
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        self.executed_queries.append(query)

    def fetchall(self):
        return self.fetch_results

    def close(self):
        self.close_called = True


class MockConnection:
    """Test stub for database connection"""

    def __init__(self):
        self.cursor_instance = MockCursor()
        self.commit_called = False
        self.rollback_called = False
        self.close_called = False
        self.rollback_should_fail = False
        self.cursor_should_return_none = False
        self.cursor_should_raise_exception = False
        self.cursor_exception_message = ""

    def cursor(self):
        if self.cursor_should_raise_exception:
            raise Exception(self.cursor_exception_message)
        if self.cursor_should_return_none:
            return None
        return self.cursor_instance

    def commit(self):
        self.commit_called = True

    def rollback(self):
        if self.rollback_should_fail:
            raise Exception("Rollback failed")
        self.rollback_called = True

    def close(self):
        self.close_called = True


class TestNamedParameterSQLTemplate:
    """Test cases for NamedParameterSQLTemplate"""

    def test_init_and_parse_params(self):
        """Test initialization and parameter parsing"""
        # Arrange & Act
        sql = "SELECT * FROM users WHERE id = :user_id AND status = :status"
        template = NamedParameterSQLTemplate(sql)

        # Assert
        assert template.sql == sql
        assert template.params_map == {'user_id': None, 'status': None}

    def test_parse_sql_for_params_no_parameters(self):
        """Test parsing SQL with no parameters"""
        # Arrange & Act
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Assert
        assert template.params_map == {}

    def test_parse_sql_for_params_multiple_same_parameter(self):
        """Test parsing SQL with the same parameter appearing multiple times"""
        # Arrange & Act
        sql = "SELECT * FROM users WHERE id = :user_id OR parent_id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Assert
        assert template.params_map == {'user_id': None}

    def test_parse_sql_for_params_complex_parameter_names(self):
        """Test parsing SQL with complex parameter names"""
        # Arrange & Act
        sql = "SELECT * FROM users WHERE id = :user_id_123 AND type = :user_type_ABC"
        template = NamedParameterSQLTemplate(sql)

        # Assert
        assert template.params_map == {'user_id_123': None, 'user_type_ABC': None}

    def test_format_with_no_params_in_sql(self):
        """Test formatting SQL with no parameters"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Act
        result = template.format()

        # Assert
        assert result == sql

    def test_format_with_params(self):
        """Test formatting SQL with parameters"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id AND status = :status"
        template = NamedParameterSQLTemplate(sql)
        params = {'user_id': 123, 'status': 'active'}

        # Act
        result = template.format(params)

        # Assert
        assert result == "SELECT * FROM users WHERE id = 123 AND status = 'active'"

    def test_format_with_integer_parameter(self):
        """Test formatting SQL with integer parameter"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)
        params = {'user_id': 123}

        # Act
        result = template.format(params)

        # Assert
        assert result == "SELECT * FROM users WHERE id = 123"

    def test_format_with_float_parameter(self):
        """Test formatting SQL with float parameter"""
        # Arrange
        sql = "SELECT * FROM products WHERE price = :price"
        template = NamedParameterSQLTemplate(sql)
        params = {'price': 99.99}

        # Act
        result = template.format(params)

        # Assert
        assert result == "SELECT * FROM products WHERE price = 99.99"

    def test_format_with_string_parameter(self):
        """Test formatting SQL with string parameter"""
        # Arrange
        sql = "SELECT * FROM users WHERE name = :name"
        template = NamedParameterSQLTemplate(sql)
        params = {'name': 'John Doe'}

        # Act
        result = template.format(params)

        # Assert
        assert result == "SELECT * FROM users WHERE name = 'John Doe'"

    def test_format_with_boolean_parameter(self):
        """Test formatting SQL with boolean parameter"""
        # Arrange
        sql = "SELECT * FROM users WHERE active = :active"
        template = NamedParameterSQLTemplate(sql)
        params = {'active': True}

        # Act
        result = template.format(params)

        # Assert - Based on actual implementation behavior
        assert result == "SELECT * FROM users WHERE active = True"

    def test_format_with_same_parameter_multiple_times(self):
        """Test formatting SQL with the same parameter appearing multiple times"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id OR parent_id = :user_id"
        template = NamedParameterSQLTemplate(sql)
        params = {'user_id': 123}

        # Act
        result = template.format(params)

        # Assert
        assert result == "SELECT * FROM users WHERE id = 123 OR parent_id = 123"

    def test_format_with_missing_params(self):
        """Test formatting SQL with missing parameters"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id AND status = :status"
        template = NamedParameterSQLTemplate(sql)
        params = {'user_id': 123}  # Missing 'status'

        # Act & Assert
        with pytest.raises(ValueError, match="Missing parameter: status"):
            template.format(params)

    def test_format_with_no_params_provided_but_required(self):
        """Test formatting SQL with no parameters provided but required"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Act & Assert
        with pytest.raises(ValueError, match="SQL contains parameters"):
            template.format()

    def test_format_with_empty_params_dict_but_required(self):
        """Test formatting SQL with empty parameters dict but required"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Act & Assert
        with pytest.raises(ValueError, match="Missing parameter: user_id"):
            template.format({})

    def test_execute_query_with_results(self):
        """Test executing a query that returns results"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Set up stub connection and cursor
        stub_conn = MockConnection()
        stub_conn.cursor_instance.description = [('id',), ('name',)]
        stub_conn.cursor_instance.fetch_results = [(1, 'John'), (2, 'Jane')]

        # Act
        result = template.execute_query(stub_conn, {'user_id': 1})

        # Assert
        assert len(stub_conn.cursor_instance.executed_queries) == 1
        assert stub_conn.cursor_instance.executed_queries[0] == "SELECT * FROM users WHERE id = 1"
        assert result == [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]
        assert stub_conn.cursor_instance.close_called == True
        assert stub_conn.close_called == False  # Connection should not be closed by default

    def test_execute_query_with_no_results(self):
        """Test executing a query that returns no results"""
        # Arrange
        sql = "UPDATE users SET status = :status WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Set up stub connection and cursor
        stub_conn = MockConnection()
        stub_conn.cursor_instance.description = None

        # Act
        result = template.execute_query(stub_conn, {'user_id': 1, 'status': 'inactive'})

        # Assert
        assert len(stub_conn.cursor_instance.executed_queries) == 1
        assert stub_conn.cursor_instance.executed_queries[0] == "UPDATE users SET status = 'inactive' WHERE id = 1"
        assert stub_conn.commit_called == True
        assert result == []

    def test_execute_query_without_params_on_parameterless_sql(self):
        """Test executing a query without parameters on SQL that doesn't need them"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Set up stub connection and cursor
        stub_conn = MockConnection()
        stub_conn.cursor_instance.description = [('id',)]
        stub_conn.cursor_instance.fetch_results = [(1,)]

        # Act
        result = template.execute_query(stub_conn)

        # Assert
        assert len(stub_conn.cursor_instance.executed_queries) == 1
        assert stub_conn.cursor_instance.executed_queries[0] == "SELECT * FROM users"
        assert result == [{'id': 1}]

    def test_execute_query_with_error(self):
        """Test executing a query that raises an error"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Set up stub connection and cursor to raise an exception
        stub_conn = MockConnection()
        stub_conn.cursor_instance.should_raise_exception = True
        stub_conn.cursor_instance.exception_message = "Database error"

        # Act & Assert
        with pytest.raises(Exception, match="SQL query execution failed: Database error"):
            template.execute_query(stub_conn, {'user_id': 1})

        assert stub_conn.rollback_called == True

    def test_execute_query_with_error_and_rollback_failure(self):
        """Test executing a query that raises an error and rollback also fails"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Set up stub connection and cursor to raise exception and rollback to fail
        stub_conn = MockConnection()
        stub_conn.cursor_instance.should_raise_exception = True
        stub_conn.cursor_instance.exception_message = "Database error"
        stub_conn.rollback_should_fail = True

        # Act & Assert
        with pytest.raises(Exception, match="SQL query execution failed: Database error"):
            template.execute_query(stub_conn, {'user_id': 1})

    def test_execute_query_with_close_conn(self):
        """Test executing a query with close_conn=True"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Set up stub connection and cursor
        stub_conn = MockConnection()
        stub_conn.cursor_instance.description = None

        # Act
        template.execute_query(stub_conn, close_conn=True)

        # Assert
        assert stub_conn.close_called == True

    def test_execute_query_with_no_connection(self):
        """Test executing a query with no connection"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Act & Assert
        with pytest.raises(ValueError, match="Database connection is required"):
            template.execute_query(None)

    def test_execute_query_format_error_with_no_params_map(self):
        """Test executing a query when format fails but params_map is empty"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)
        # Force params_map to be empty
        template.params_map = {}

        # Set up stub connection
        stub_conn = MockConnection()
        stub_conn.cursor_instance.description = None

        # Act
        result = template.execute_query(stub_conn, {'unexpected_param': 'value'})

        # Assert - should use raw SQL when format fails and no params expected
        assert stub_conn.cursor_instance.executed_queries[0] == sql
        assert result == []

    def test_execute_query_with_cursor_none(self):
        """Test executing a query where cursor could be None in finally block"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Create a stub connection that returns None for cursor
        stub_conn = MockConnection()
        stub_conn.cursor_should_return_none = True

        # Act & Assert - This should raise an Exception about SQL query execution failed
        with pytest.raises(Exception, match="SQL query execution failed"):
            template.execute_query(stub_conn)

    def test_execute_query_cursor_creation_failure(self):
        """Test that cursor creation failure is handled properly without UnboundLocalError"""
        # Arrange
        sql = "SELECT * FROM users WHERE id = :user_id"
        template = NamedParameterSQLTemplate(sql)

        # Create a stub connection that will fail cursor creation
        stub_conn = MockConnection()
        stub_conn.cursor_should_raise_exception = True
        stub_conn.cursor_exception_message = "Cursor creation failed"

        # Act & Assert - Should get SQL execution error, not UnboundLocalError
        with pytest.raises(Exception, match="SQL query execution failed: Cursor creation failed"):
            template.execute_query(stub_conn, {'user_id': 1})

    def test_execute_query_with_none_connection_in_finally(self):
        """Test finally block with None connection when close_conn=True"""
        # Arrange
        sql = "SELECT * FROM users"
        template = NamedParameterSQLTemplate(sql)

        # Act & Assert - This should not raise an exception
        with pytest.raises(ValueError, match="Database connection is required"):
            template.execute_query(None, close_conn=True)
