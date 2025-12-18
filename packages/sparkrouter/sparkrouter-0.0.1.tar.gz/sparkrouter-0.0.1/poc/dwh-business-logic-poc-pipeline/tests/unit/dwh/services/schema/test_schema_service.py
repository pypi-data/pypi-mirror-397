import pytest
from pyspark.sql.types import StringType, IntegerType, LongType, TimestampType, BooleanType, DecimalType

from dwh.services.schema.schema_service import DDLSchemaService


class MockDDLFileReader:
    """Mock DDL file reader for testing"""

    def __init__(self, ddl_content: str):
        self.ddl_content = ddl_content

    def read_ddl_file(self, schema_ref: str) -> str:
        return self.ddl_content


class TestDDLSchemaService:
    
    def test_get_schema_basic_table(self):
        """Test basic schema extraction from DDL"""
        ddl_content = """
        CREATE TABLE test_table (
            id INTEGER NOT NULL,
            name VARCHAR(255),
            active BOOLEAN
        );
        """
        
        file_reader = MockDDLFileReader(ddl_content)
        service = DDLSchemaService(file_reader)
        
        schema = service.get_schema("test_schema.ddl", "test_table")
        
        assert len(schema.fields) == 3
        assert schema.fields[0].name == "id"
        assert isinstance(schema.fields[0].dataType, IntegerType)
        assert not schema.fields[0].nullable
        
        assert schema.fields[1].name == "name"
        assert isinstance(schema.fields[1].dataType, StringType)
        assert schema.fields[1].nullable
        
        assert schema.fields[2].name == "active"
        assert isinstance(schema.fields[2].dataType, BooleanType)
        assert schema.fields[2].nullable
    
    def test_get_schema_with_various_types(self):
        """Test schema extraction with various SQL types"""
        ddl_content = """
        CREATE TABLE complex_table (
            id BIGINT NOT NULL,
            name TEXT,
            price DECIMAL(10,2),
            created_at TIMESTAMP,
            description STRING
        );
        """
        
        file_reader = MockDDLFileReader(ddl_content)
        service = DDLSchemaService(file_reader)
        
        schema = service.get_schema("test_schema.ddl", "complex_table")
        
        assert len(schema.fields) == 5
        assert isinstance(schema.fields[0].dataType, LongType)  # BIGINT
        assert isinstance(schema.fields[1].dataType, StringType)  # TEXT
        assert isinstance(schema.fields[2].dataType, DecimalType)  # DECIMAL
        assert isinstance(schema.fields[3].dataType, TimestampType)  # TIMESTAMP
        assert isinstance(schema.fields[4].dataType, StringType)  # STRING
    
    def test_get_schema_caching(self):
        """Test that schemas are cached properly"""
        ddl_content = """
        CREATE TABLE cached_table (
            id INTEGER,
            name VARCHAR(100)
        );
        """
        
        file_reader = MockDDLFileReader(ddl_content)
        service = DDLSchemaService(file_reader)
        
        # First call
        schema1 = service.get_schema("test_schema.ddl", "cached_table")
        
        # Second call should return cached version
        schema2 = service.get_schema("test_schema.ddl", "cached_table")
        
        assert schema1 is schema2  # Same object reference
        assert len(service.schema_cache) == 1
    
    def test_get_schema_table_not_found(self):
        """Test error when table not found in DDL"""
        ddl_content = """
        CREATE TABLE existing_table (
            id INTEGER
        );
        """
        
        file_reader = MockDDLFileReader(ddl_content)
        service = DDLSchemaService(file_reader)
        
        with pytest.raises(ValueError, match="Table nonexistent_table not found in DDL"):
            service.get_schema("test_schema.ddl", "nonexistent_table")
    
    def test_map_sql_type_to_spark(self):
        """Test SQL type mapping to Spark types"""
        file_reader = MockDDLFileReader("")
        service = DDLSchemaService(file_reader)
        
        assert isinstance(service._map_sql_type_to_spark("VARCHAR(255)"), StringType)
        assert isinstance(service._map_sql_type_to_spark("TEXT"), StringType)
        assert isinstance(service._map_sql_type_to_spark("INTEGER"), IntegerType)
        assert isinstance(service._map_sql_type_to_spark("BIGINT"), LongType)
        assert isinstance(service._map_sql_type_to_spark("TIMESTAMP"), TimestampType)
        assert isinstance(service._map_sql_type_to_spark("BOOLEAN"), BooleanType)
        assert isinstance(service._map_sql_type_to_spark("DECIMAL"), DecimalType)
        assert isinstance(service._map_sql_type_to_spark("UNKNOWN_TYPE"), StringType)  # Fallback
