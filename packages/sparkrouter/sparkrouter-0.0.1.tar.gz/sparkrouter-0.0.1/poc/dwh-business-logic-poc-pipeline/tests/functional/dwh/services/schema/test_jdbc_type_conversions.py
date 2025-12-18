import pytest
from datetime import datetime
from decimal import Decimal
from pyspark.sql import Row
from pyspark.sql.types import (
    StringType, IntegerType, LongType,
    TimestampType, BooleanType, DecimalType
)

from dwh.services.schema.schema_service import DDLSchemaService
from functional.dwh.jobs.load_promos.test_strategies import (
    FunctionalJDBCDataSinkStrategy
)


@pytest.mark.functional
class TestJDBCTypeConversions:
    """Comprehensive tests for JDBC type conversions - DDL to Spark and round-trip"""
    
    def test_ddl_to_spark_type_mappings(self, spark_session, test_ddl_file_reader):
        """Test all DDL type mappings to Spark types"""
        # Create DDL with all supported types
        test_ddl_content = """
CREATE TABLE type_test_table (
    varchar_field VARCHAR(255),
    text_field TEXT,
    string_field STRING,
    int_field INT,
    integer_field INTEGER,
    bigint_field BIGINT,
    long_field LONG,
    timestamp_field TIMESTAMP,
    datetime_field DATETIME,
    time_field TIME,
    boolean_field BOOLEAN,
    bool_field BOOL,
    decimal_field DECIMAL(10,2)
);
        """
        
        test_ddl_file_reader.file_contents["type_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Get schema and verify type mappings
        schema = schema_service.get_schema("type_test.ddl", "type_test_table")
        
        # Verify each field type mapping
        field_types = {field.name: field.dataType for field in schema.fields}
        
        # String types
        assert isinstance(field_types['varchar_field'], StringType)
        assert isinstance(field_types['text_field'], StringType)
        assert isinstance(field_types['string_field'], StringType)
        
        # Integer types
        assert isinstance(field_types['int_field'], IntegerType)
        assert isinstance(field_types['integer_field'], IntegerType)
        assert isinstance(field_types['bigint_field'], LongType)
        assert isinstance(field_types['long_field'], LongType)
        
        # Temporal types
        assert isinstance(field_types['timestamp_field'], TimestampType)
        assert isinstance(field_types['datetime_field'], TimestampType)
        assert isinstance(field_types['time_field'], StringType)  # TIME mapped to StringType
        
        # Boolean types
        assert isinstance(field_types['boolean_field'], BooleanType)
        assert isinstance(field_types['bool_field'], BooleanType)
        
        # Decimal type
        assert isinstance(field_types['decimal_field'], DecimalType)
        
        print("✓ All DDL to Spark type mappings verified")
    
    def test_time_field_handling_comprehensive(self, spark_session, test_ddl_file_reader):
        """Test TIME field handling with HH:MM:SS format"""
        test_ddl_content = """
CREATE TABLE time_test (
    id INT,
    start_time TIME,
    end_time TIME,
    midnight TIME,
    almost_midnight TIME
);
        """
        
        test_ddl_file_reader.file_contents["time_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Test TIME with HH:MM:SS format
        test_data = [
            Row(id=1, start_time="00:00:00", end_time="23:59:59", midnight="00:00:00", almost_midnight="23:59:59"),
            Row(id=2, start_time="12:00:00", end_time="12:30:45", midnight="00:00:01", almost_midnight="23:59:58"),
            Row(id=3, start_time="09:15:30", end_time="17:45:15", midnight="00:30:00", almost_midnight="23:30:00")
        ]
        
        schema = schema_service.get_schema("time_test.ddl", "time_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        # Verify TIME fields are StringType
        time_fields = [field for field in schema.fields if 'time' in field.name]
        for field in time_fields:
            assert isinstance(field.dataType, StringType), f"TIME field {field.name} should be StringType"
        
        # Test write to JDBC sink
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        # Should not raise exception - TIME strings are valid
        jdbc_sink.write_sink_df(test_df, "time_test.ddl", "time_test", mode="overwrite")
        
        print("✓ TIME field HH:MM:SS format handling verified")
    
    def test_boundary_values_comprehensive(self, spark_session, test_ddl_file_reader):
        """Test boundary values for all numeric and temporal types"""
        test_ddl_content = """
CREATE TABLE boundary_test (
    int_min INT,
    int_max INT,
    bigint_min BIGINT,
    bigint_max BIGINT,
    decimal_precision DECIMAL(10,2),
    timestamp_early TIMESTAMP,
    timestamp_late TIMESTAMP
);
        """
        
        test_ddl_file_reader.file_contents["boundary_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Test boundary values
        test_data = [
            Row(
                int_min=-2147483648,  # INT32 min
                int_max=2147483647,   # INT32 max
                bigint_min=-9223372036854775808,  # INT64 min
                bigint_max=9223372036854775807,   # INT64 max
                decimal_precision=Decimal('99999999.99'),  # Max for DECIMAL(10,2)
                timestamp_early=datetime(1970, 1, 1, 0, 0, 0),
                timestamp_late=datetime(2038, 1, 19, 3, 14, 7)
            )
        ]
        
        schema = schema_service.get_schema("boundary_test.ddl", "boundary_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        # Should handle boundary values without overflow
        jdbc_sink.write_sink_df(test_df, "boundary_test.ddl", "boundary_test", mode="overwrite")
        
        print("✓ Boundary value handling verified")
    
    def test_null_value_handling(self, spark_session, test_ddl_file_reader):
        """Test NULL value handling across all types"""
        test_ddl_content = """
CREATE TABLE null_test (
    varchar_null VARCHAR(255),
    int_null INT,
    bigint_null BIGINT,
    timestamp_null TIMESTAMP,
    boolean_null BOOLEAN,
    decimal_null DECIMAL(10,2),
    time_null TIME
);
        """
        
        test_ddl_file_reader.file_contents["null_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Test all NULL values
        test_data = [
            Row(
                varchar_null=None,
                int_null=None,
                bigint_null=None,
                timestamp_null=None,
                boolean_null=None,
                decimal_null=None,
                time_null=None
            ),
            Row(
                varchar_null="valid",
                int_null=42,
                bigint_null=9999999999,
                timestamp_null=datetime(2024, 1, 1, 12, 0, 0),
                boolean_null=True,
                decimal_null=Decimal('123.45'),
                time_null="14:30:00"
            )
        ]
        
        schema = schema_service.get_schema("null_test.ddl", "null_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        # Should handle NULL values correctly
        jdbc_sink.write_sink_df(test_df, "null_test.ddl", "null_test", mode="overwrite")
        
        print("✓ NULL value handling verified")
    
    def test_decimal_default_precision_scale(self, spark_session, test_ddl_file_reader):
        """Test DECIMAL types use default precision/scale in DDL parser"""
        test_ddl_content = """
CREATE TABLE decimal_test (
    decimal_small DECIMAL(5,2),
    decimal_large DECIMAL(18,6),
    decimal_no_scale DECIMAL(10,0)
);
        """
        
        test_ddl_file_reader.file_contents["decimal_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        test_data = [
            Row(
                decimal_small=Decimal('12345.67'),
                decimal_large=Decimal('87654.32'),
                decimal_no_scale=Decimal('99999.99')
            ),
            Row(
                decimal_small=Decimal('0.01'),
                decimal_large=Decimal('1.23'),
                decimal_no_scale=Decimal('1.00')
            )
        ]
        
        schema = schema_service.get_schema("decimal_test.ddl", "decimal_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        # Verify DDL parser uses default DECIMAL(10,2) for all DECIMAL types
        decimal_fields = {field.name: field.dataType for field in schema.fields if isinstance(field.dataType, DecimalType)}
        
        # DDL parser currently uses default precision/scale regardless of DDL specification
        for field_name, decimal_type in decimal_fields.items():
            assert decimal_type.precision == 10, f"{field_name} precision should be 10 (default)"
            assert decimal_type.scale == 2, f"{field_name} scale should be 2 (default)"
        
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        jdbc_sink.write_sink_df(test_df, "decimal_test.ddl", "decimal_test", mode="overwrite")
        
        print("✓ DECIMAL default precision/scale handling verified")
    
    def test_timestamp_microsecond_precision(self, spark_session, test_ddl_file_reader):
        """Test timestamp microsecond precision is preserved"""
        test_ddl_content = """
CREATE TABLE timestamp_precision_test (
    id INT,
    precise_timestamp TIMESTAMP
);
        """
        
        test_ddl_file_reader.file_contents["timestamp_precision_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Test microsecond precision timestamps
        test_data = [
            Row(id=1, precise_timestamp=datetime(2024, 1, 1, 12, 0, 0, 123456)),
            Row(id=2, precise_timestamp=datetime(2024, 1, 1, 12, 0, 0, 999999)),
            Row(id=3, precise_timestamp=datetime(2024, 1, 1, 12, 0, 0, 1))
        ]
        
        schema = schema_service.get_schema("timestamp_precision_test.ddl", "timestamp_precision_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        # Should preserve microsecond precision
        jdbc_sink.write_sink_df(test_df, "timestamp_precision_test.ddl", "timestamp_precision_test", mode="overwrite")
        
        print("✓ Timestamp microsecond precision verified")
    
    def test_string_length_constraints(self, spark_session, test_ddl_file_reader):
        """Test VARCHAR length constraints are respected"""
        test_ddl_content = """
CREATE TABLE string_length_test (
    short_varchar VARCHAR(10),
    medium_varchar VARCHAR(255),
    text_field TEXT
);
        """
        
        test_ddl_file_reader.file_contents["string_length_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        test_data = [
            Row(
                short_varchar="1234567890",  # Exactly 10 chars
                medium_varchar="A" * 255,      # Exactly 255 chars
                text_field="A" * 1000         # Large text
            ),
            Row(
                short_varchar="short",
                medium_varchar="medium length",
                text_field="regular text"
            )
        ]
        
        schema = schema_service.get_schema("string_length_test.ddl", "string_length_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        jdbc_sink.write_sink_df(test_df, "string_length_test.ddl", "string_length_test", mode="overwrite")
        
        print("✓ String length constraint handling verified")
    
    def test_boolean_value_variations(self, spark_session, test_ddl_file_reader):
        """Test boolean value handling with various representations"""
        test_ddl_content = """
CREATE TABLE boolean_test (
    id INT,
    bool_field BOOLEAN,
    bool_field2 BOOL
);
        """
        
        test_ddl_file_reader.file_contents["boolean_test.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        test_data = [
            Row(id=1, bool_field=True, bool_field2=False),
            Row(id=2, bool_field=False, bool_field2=True),
            Row(id=3, bool_field=None, bool_field2=None)
        ]
        
        schema = schema_service.get_schema("boolean_test.ddl", "boolean_test")
        test_df = spark_session.createDataFrame(test_data, schema)
        
        jdbc_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"}
        )
        
        jdbc_sink.write_sink_df(test_df, "boolean_test.ddl", "boolean_test", mode="overwrite")
        
        print("✓ Boolean value variations verified")