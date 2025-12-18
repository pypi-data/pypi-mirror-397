"""
Validators for integration test results
"""
import os
import json
# import sqlalchemy
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ResultValidator(ABC):
    """Base class for result validators"""

    @abstractmethod
    def validate(self, expected: Dict[str, Any]) -> bool:
        """Validate results against expected values"""
        pass


class FileResultValidator(ResultValidator):
    """Validator for file-based results"""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def validate(self, expected: Dict[str, Any]) -> bool:
        """Validate file results against expected values"""
        # Get file path
        file_path = os.path.join(self.base_dir, expected["path"])

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        # Check file format and validate accordingly
        file_format = expected.get("format", "").lower()

        if file_format == "json":
            return self._validate_json(file_path, expected)
        elif file_format == "csv":
            return self._validate_csv(file_path, expected)
        elif file_format == "parquet":
            return self._validate_parquet(file_path, expected)
        else:
            print(f"Unsupported file format: {file_format}")
            return False

    def _validate_json(self, file_path: str, expected: Dict[str, Any]) -> bool:
        """Validate JSON file"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Check fields if specified
            if "fields" in expected:
                for key, value in expected["fields"].items():
                    if key not in data or data[key] != value:
                        print(f"Field mismatch: {key}")
                        return False

            return True
        except Exception as e:
            print(f"Error validating JSON: {str(e)}")
            return False

    def _validate_csv(self, file_path: str, expected: Dict[str, Any]) -> bool:
        """Validate CSV file"""
        try:
            df = pd.read_csv(file_path)
            return self._validate_dataframe(df, expected)
        except Exception as e:
            print(f"Error validating CSV: {str(e)}")
            return False

    def _validate_parquet(self, file_path: str, expected: Dict[str, Any]) -> bool:
        """Validate Parquet file"""
        try:
            df = pd.read_parquet(file_path)
            return self._validate_dataframe(df, expected)
        except Exception as e:
            print(f"Error validating Parquet: {str(e)}")
            return False

    def _validate_dataframe(self, df: pd.DataFrame, expected: Dict[str, Any]) -> bool:
        """Validate DataFrame against expected values"""
        # Check row count if specified
        if "row_count" in expected and df.shape[0] != expected["row_count"]:
            print(f"Row count mismatch: expected {expected['row_count']}, got {df.shape[0]}")
            return False

        # Check columns if specified
        if "columns" in expected:
            for col in expected["columns"]:
                if col not in df.columns:
                    print(f"Column not found: {col}")
                    return False

        return True

# class DatabaseResultValidator(ResultValidator):
#     """Validator for database query results"""
#
#     def __init__(self, connection_string: str):
#         self.connection_string = connection_string
#         self.engine = sqlalchemy.create_engine(connection_string)
#
#     def validate(self, expected: Dict[str, Any]) -> bool:
#         """Validate database results against expected values"""
#         try:
#             # Execute query
#             query = expected["query"]
#             with self.engine.connect() as conn:
#                 result = conn.execute(sqlalchemy.text(query))
#                 rows = result.fetchall()
#
#             # Check row count if specified
#             if "row_count" in expected and len(rows) != expected["row_count"]:
#                 print(f"Row count mismatch: expected {expected['row_count']}, got {len(rows)}")
#                 return False
#
#             # Check values if specified
#             if "values" in expected and rows:
#                 row = rows[0]
#                 for key, value in expected["values"].items():
#                     if key not in row._mapping or row._mapping[key] != value:
#                         print(f"Value mismatch for {key}: expected {value}, got {row._mapping.get(key)}")
#                         return False
#
#             return True
#         except Exception as e:
#             print(f"Error validating database results: {str(e)}")
#             return False
