import pytest
from utils.test_ddl_file_reader import DDLFileReaderForTesting
from dwh.services.schema.schema_service import DDLSchemaService


@pytest.fixture
def test_ddl_file_reader():
    """Fixture providing TestDDLFileReader instance"""
    return DDLFileReaderForTesting()


@pytest.fixture
def schema_service(test_ddl_file_reader):
    """Fixture providing DDLSchemaService with test DDL file reader"""
    return DDLSchemaService(test_ddl_file_reader)