import re
from typing import Dict, Any, Optional


class SQLTemplateExecutionError(Exception):
    """Custom exception for SQL template execution errors"""
    pass


class NamedParameterSQLTemplate:

    def __init__(self, sql):
        self.sql = sql
        self.params_map = self._parse_sql_for_params()

    def _parse_sql_for_params(self) -> Dict[str, Any]:
        # Use regex to find all named parameters in the format :param_name
        pattern = re.compile(r':(\w+)')
        params = pattern.findall(self.sql)
        return {param: None for param in params}

    def format(self, params: Optional[Dict[str, Any]] = None) -> str:
        # If no parameters are provided but the SQL has parameters, raise an error
        if params is None:
            if self.params_map:
                # Only raise an error if there are actually parameters in the SQL
                param_list = ', '.join(self.params_map.keys())
                raise ValueError(f"SQL contains parameters ({param_list}) but no values were provided")
            return self.sql  # No parameters to replace

        # Validate that all named parameters have been declared
        for param in self.params_map.keys():
            if param not in params:
                raise ValueError(f"Missing parameter: {param}")

        # Helper for identifier validation
        def is_safe_identifier(identifier: str) -> bool:
            # Only allow alphanumeric, underscore, and dot (for schema.table)
            return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', identifier))

        # Replace all named parameters in SQL with values
        formatted_sql = self.sql
        identifier_params = {'stage', 'base'}
        for param, value in params.items():
            if param in identifier_params:
                if not is_safe_identifier(value):
                    raise ValueError(f"Unsafe identifier for SQL: {value}")
                formatted_sql = formatted_sql.replace(f":{param}", str(value))
            elif not isinstance(value, (int, float)):
                value = f"'{value}'"  # Add quotes around string values
                formatted_sql = formatted_sql.replace(f":{param}", str(value))
            else:
                formatted_sql = formatted_sql.replace(f":{param}", str(value))
        return formatted_sql

    def execute_query(
            self,
            conn: Any,
            params: Optional[Dict[str, Any]] = None,
            close_conn: bool = False) -> Any:
        if conn is None:
            raise ValueError("Database connection is required")

        # Initialize formatted_query to avoid UnboundLocalError
        try:
            formatted_query = self.format(params)
        except ValueError as e:
            # If the SQL has no parameters but we're trying to use parameters, just use the raw SQL
            if "SQL contains parameters" in str(e) and not self.params_map:
                formatted_query = self.sql
            else:
                # Re-raise the ValueError if it's not about missing parameters
                raise e

        cursor = None  # Initialize cursor to None to avoid UnboundLocalError
        try:
            cursor = conn.cursor()
            cursor.execute(formatted_query)

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return result

            conn.commit()
            return []
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass  # Some connections might not support rollback
            raise Exception(f"SQL query execution failed: {str(e)}")
        finally:
            try:
                if cursor:
                    cursor.close()
                if close_conn and conn:
                    conn.close()
            except UnboundLocalError:
                # This should not happen anymore since we initialize cursor to None
                # But if it does, raise our custom exception for consistent error handling
                raise SQLTemplateExecutionError("Failed to properly handle database cursor cleanup")
