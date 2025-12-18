"""Simple DDL parsing test without Spark dependencies"""

import unittest
from dwh.services.schema.schema_service import DDLSchemaService
from dwh.services.file.ddl_file_reader import DDLFileReader


class NoopDDLFileReader(DDLFileReader):
    """Noop DDL file reader for testing"""
    
    def read_ddl_file(self, schema_ref: str, table_name: str) -> str:
        """Return empty DDL for testing"""
        return "CREATE TABLE test (id VARCHAR(255));"


class TestDDLParsingSimple(unittest.TestCase):
    """Test DDL parsing logic without Spark session"""

    def test_parse_field_definitions(self):
        """Test field definition parsing"""
        # Create service with noop file reader
        noop_reader = NoopDDLFileReader()
        service = DDLSchemaService(noop_reader)
        
        # Test simple field definitions
        columns_section = """
            _id VARCHAR(255) NOT NULL,
            name VARCHAR(100),
            updatedate TIMESTAMP,
            ptn_ingress_date VARCHAR(10)
        """
        
        fields = service._parse_field_definitions(columns_section)
        
        # Should have 4 fields
        self.assertEqual(len(fields), 4)
        self.assertIn('_id VARCHAR(255) NOT NULL', fields)
        self.assertIn('name VARCHAR(100)', fields)
        self.assertIn('updatedate TIMESTAMP', fields)
        self.assertIn('ptn_ingress_date VARCHAR(10)', fields)

    def test_parse_single_field(self):
        """Test single field parsing"""
        noop_reader = NoopDDLFileReader()
        service = DDLSchemaService(noop_reader)
        
        # Test basic field
        field_def = "_id VARCHAR(255) NOT NULL"
        field = service._parse_single_field(field_def)
        
        self.assertIsNotNone(field)
        self.assertEqual(field.name, "_id")
        self.assertFalse(field.nullable)  # NOT NULL
        
        # Test nullable field
        field_def = "name VARCHAR(100)"
        field = service._parse_single_field(field_def)
        
        self.assertIsNotNone(field)
        self.assertEqual(field.name, "name")
        self.assertTrue(field.nullable)  # Default nullable

    def test_map_sql_type_to_spark(self):
        """Test SQL type mapping"""
        noop_reader = NoopDDLFileReader()
        service = DDLSchemaService(noop_reader)
        
        from pyspark.sql.types import StringType, IntegerType, LongType, TimestampType
        
        # Test various type mappings
        self.assertIsInstance(service._map_sql_type_to_spark("VARCHAR(255)"), StringType)
        self.assertIsInstance(service._map_sql_type_to_spark("TEXT"), StringType)
        self.assertIsInstance(service._map_sql_type_to_spark("INT"), IntegerType)
        self.assertIsInstance(service._map_sql_type_to_spark("BIGINT"), LongType)
        self.assertIsInstance(service._map_sql_type_to_spark("TIMESTAMP"), TimestampType)


if __name__ == '__main__':
    unittest.main()