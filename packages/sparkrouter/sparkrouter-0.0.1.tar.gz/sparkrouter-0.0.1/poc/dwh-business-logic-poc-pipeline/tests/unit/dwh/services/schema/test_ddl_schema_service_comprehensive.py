"""
Comprehensive tests for DDL Schema Service to identify parsing issues.

These tests will expose what's broken in the DDL parsing logic.
"""
from dwh.services.schema.schema_service import DDLSchemaService
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class TestDDLSchemaServiceComprehensive:
    """Comprehensive tests to identify DDL schema service issues"""
    
    def test_ddl_file_exists_and_readable(self, test_ddl_file_reader):
        """Test that DDL file exists and can be read"""
        ddl_content = test_ddl_file_reader.read_ddl_file(LoadPromosSchema.SOURCE_SCHEMA_REF)
        
        assert ddl_content is not None
        assert len(ddl_content) > 0
        assert "CREATE TABLE" in ddl_content
        assert "ecom_sflycompromotion_promotions" in ddl_content
        print(f"DDL file content length: {len(ddl_content)} characters")
    
    def test_ddl_content_structure(self, test_ddl_file_reader):
        """Test DDL content has expected structure"""
        ddl_content = test_ddl_file_reader.read_ddl_file(LoadPromosSchema.SOURCE_SCHEMA_REF)
        
        # Check for key fields that should exist
        assert "_id VARCHAR(255)" in ddl_content
        assert "name VARCHAR(255)" in ddl_content
        assert "discount_discountTiers STRUCT<" in ddl_content
        assert "bundles_bundleA STRUCT<" in ddl_content
        assert "properties_flags STRUCT<" in ddl_content
        
        print("DDL Content Preview:")
        print(ddl_content[:500] + "...")
    
    def test_schema_service_basic_parsing(self, test_ddl_file_reader):
        """Test basic schema service parsing"""
        schema_service = DDLSchemaService(test_ddl_file_reader)
        schema = schema_service.get_schema(
            LoadPromosSchema.SOURCE_SCHEMA_REF,
            LoadPromosSchema.SOURCE_TABLE_NAME
        )
        
        assert schema is not None
        assert len(schema.fields) > 0
        
        print(f"Parsed schema has {len(schema.fields)} fields")
        print("First 10 fields:")
        for i, field in enumerate(schema.fields[:10]):
            print(f"  {i+1}. {field.name} ({field.dataType})")
    
    def test_schema_field_names_match_ddl(self, test_ddl_file_reader):
        """Test that schema field names match what's in DDL"""
        ddl_content = test_ddl_file_reader.read_ddl_file(LoadPromosSchema.SOURCE_SCHEMA_REF)
        schema_service = DDLSchemaService(test_ddl_file_reader)
        schema = schema_service.get_schema(
            LoadPromosSchema.SOURCE_SCHEMA_REF,
            LoadPromosSchema.SOURCE_TABLE_NAME
        )
        
        # Extract field names from DDL manually
        ddl_lines = [line.strip() for line in ddl_content.split('\n') if line.strip() and not line.strip().startswith('--')]
        ddl_field_lines = [line for line in ddl_lines if ' ' in line and not line.startswith('CREATE') and not line.startswith(');')]
        
        print("DDL Field Lines:")
        for line in ddl_field_lines[:10]:
            print(f"  {line}")
        
        print("\nParsed Schema Fields:")
        for field in schema.fields[:10]:
            print(f"  {field.name}")
        
        # Check if _id field exists in schema
        field_names = [field.name for field in schema.fields]
        assert "_id" in field_names, f"_id field missing from schema. Fields: {field_names[:10]}"
    
    def test_nested_structure_parsing(self, test_ddl_file_reader):
        """Test how nested structures are parsed"""
        schema_service = DDLSchemaService(test_ddl_file_reader)
        schema = schema_service.get_schema(
            LoadPromosSchema.SOURCE_SCHEMA_REF,
            LoadPromosSchema.SOURCE_TABLE_NAME
        )
        
        # Look for nested structure fields
        nested_fields = []
        for field in schema.fields:
            if "discount" in field.name.lower() or "bundle" in field.name.lower() or "properties_flags" in field.name:
                nested_fields.append(field)
        
        print("Nested structure fields found:")
        for field in nested_fields:
            print(f"  {field.name}: {field.dataType}")
        
        # Check if nested structures are flattened incorrectly
        duplicate_names = {}
        for field in schema.fields:
            if field.name in duplicate_names:
                duplicate_names[field.name] += 1
            else:
                duplicate_names[field.name] = 1
        
        duplicates = {name: count for name, count in duplicate_names.items() if count > 1}
        if duplicates:
            print(f"ISSUE: Duplicate field names found: {duplicates}")
            assert False, f"Schema has duplicate field names: {duplicates}"
    
    def test_schema_field_count_expectation(self, test_ddl_file_reader):
        """Test expected field count vs actual"""
        ddl_content = test_ddl_file_reader.read_ddl_file(LoadPromosSchema.SOURCE_SCHEMA_REF)
        schema_service = DDLSchemaService(test_ddl_file_reader)
        schema = schema_service.get_schema(
            LoadPromosSchema.SOURCE_SCHEMA_REF,
            LoadPromosSchema.SOURCE_TABLE_NAME
        )
        
        # Count field definitions in DDL (rough estimate)
        field_lines = [line for line in ddl_content.split('\n') 
                      if line.strip() and not line.strip().startswith('--') 
                      and not line.strip().startswith('CREATE')
                      and not line.strip().startswith(');')
                      and ' ' in line.strip()]
        
        print(f"DDL appears to have ~{len(field_lines)} field definitions")
        print(f"Schema service parsed {len(schema.fields)} fields")
        
        # This test will help us understand the discrepancy
        if len(schema.fields) != len(field_lines):
            print("DISCREPANCY DETECTED:")
            print(f"  Expected ~{len(field_lines)} fields from DDL")
            print(f"  Got {len(schema.fields)} fields from schema service")
    
    def test_compare_with_working_schema(self, test_ddl_file_reader):
        """Compare DDL schema with working hardcoded schema from other tests"""
        schema_service = DDLSchemaService(test_ddl_file_reader)
        ddl_schema = schema_service.get_schema(
            LoadPromosSchema.SOURCE_SCHEMA_REF,
            LoadPromosSchema.SOURCE_TABLE_NAME
        )
        
        # Expected fields from working test (first 10)
        expected_fields = [
            "_id", "name", "description", "ptn_ingress_date", "updatedate", 
            "createDate", "properties_promotionType", "properties_redemptionMethod",
            "properties_periscopeId", "properties_flags"
        ]
        
        ddl_field_names = [field.name for field in ddl_schema.fields]
        
        print("Expected vs Actual field comparison:")
        for expected in expected_fields:
            if expected in ddl_field_names:
                print(f"  + {expected} - FOUND")
            else:
                print(f"  - {expected} - MISSING")
        
        print(f"\nFirst 10 DDL fields: {ddl_field_names[:10]}")
        
        # Check for critical missing fields
        missing_critical = [field for field in ["_id", "name", "properties_promotionType"] 
                          if field not in ddl_field_names]
        
        if missing_critical:
            assert False, f"Critical fields missing from DDL schema: {missing_critical}"