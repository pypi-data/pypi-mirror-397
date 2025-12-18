"""
Test utilities for consistent test execution across different environments.

This module provides utilities that work regardless of where tests are executed from
(PyCharm, command line, CI/CD, etc.).
"""

import os
from contextlib import contextmanager


def find_business_logic_root():
    """
    Find the business-logic root directory by looking for schemas folder.
    
    Walks up the directory tree from the current file location until it finds
    a directory containing a 'schemas' folder, which indicates the business-logic root.
    
    Returns:
        str: Absolute path to the business-logic root directory
        
    Raises:
        FileNotFoundError: If schemas folder cannot be found in any parent directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        schemas_dir = os.path.join(current_dir, 'schemas')
        if os.path.exists(schemas_dir) and os.path.isdir(schemas_dir):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    raise FileNotFoundError("Could not find business-logic root directory with schemas folder")


@contextmanager
def business_logic_context():
    """
    Context manager that temporarily changes to business-logic root directory.
    
    This ensures schema files and other resources can be found regardless of
    where the test is executed from.
    
    Usage:
        with business_logic_context():
            # Code that needs access to schemas/ and other business-logic resources
            schema_service = DDLSchemaService(DDLFileReader)
    """
    original_cwd = os.getcwd()
    business_logic_dir = find_business_logic_root()
    os.chdir(business_logic_dir)
    try:
        yield business_logic_dir
    finally:
        os.chdir(original_cwd)