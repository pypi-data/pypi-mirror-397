from abc import ABC, abstractmethod
import re
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StructField, StructType, ArrayType
)

from dwh.services.schema.spark_jdbc_mapper import SparkJDBCMapper


class SchemaService(ABC):
    """Abstract service for schema operations"""
    
    @abstractmethod
    def get_schema(self, schema_ref: str, table_name: str) -> StructType:
        """Get Spark schema for a specific table from a schema reference"""
        pass


class DDLSchemaService(SchemaService):
    """Schema service that reads from DDL files"""
    
    def __init__(self, file_reader):
        self.file_reader = file_reader
        self.schema_cache = {}
    
    def get_schema(self, schema_ref: str, table_name: str) -> StructType:
        """Get Spark schema from DDL file"""
        cache_key = f"{schema_ref}:{table_name}"
        
        if cache_key in self.schema_cache:
            return self.schema_cache[cache_key]
        
        # Read DDL file and convert to Spark schema
        ddl_content = self.file_reader.read_ddl_file(schema_ref)
        spark_schema = self._convert_ddl_to_spark_schema(ddl_content, table_name)
        
        self.schema_cache[cache_key] = spark_schema
        return spark_schema

    def _convert_ddl_to_spark_schema(self, ddl_content: str, table_name: str) -> StructType:
        """Convert DDL content to Spark StructType"""
        # Extract CREATE TABLE section for the specific table
        # Handle both simple tables and tables with TBLPROPERTIES/USING/PARTITIONED BY
        table_pattern = rf'CREATE\s+TABLE[^(]*{re.escape(table_name)}\s*\((.*?)\)(?:\s*USING|\s*PARTITIONED|\s*TBLPROPERTIES|\s*;|$)'
        match = re.search(table_pattern, ddl_content, re.IGNORECASE | re.DOTALL)

        if not match:
            raise ValueError(f"Table {table_name} not found in DDL")

        columns_section = match.group(1)
        fields = []

        # Parse field definitions properly handling nested structures
        field_definitions = self._parse_field_definitions(columns_section)

        for field_def in field_definitions:
            if not field_def.strip() or field_def.strip().startswith('--'):
                continue

            field = self._parse_single_field(field_def)
            if field:
                fields.append(field)

        return StructType(fields)

    def _parse_field_definitions(self, columns_section: str) -> list:  # noqa: C901
        """Parse field definitions handling nested structures correctly"""
        # Remove comments first
        lines = columns_section.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove inline comments
            line = re.sub(r'--.*$', '', line)
            if line.strip():
                cleaned_lines.append(line)
        
        # Rejoin without comments
        cleaned_content = '\n'.join(cleaned_lines)
        
        fields = []
        current_field = ""
        paren_depth = 0
        angle_depth = 0

        for char in cleaned_content:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '<':
                angle_depth += 1
            elif char == '>':
                angle_depth -= 1
            elif char == ',' and paren_depth == 0 and angle_depth == 0:
                # End of field definition
                if current_field.strip():
                    fields.append(current_field.strip())
                current_field = ""
                continue

            current_field += char

        # Add the last field
        if current_field.strip():
            fields.append(current_field.strip())

        return fields

    def _parse_single_field(self, field_def: str):
        """Parse a single field definition"""
        # Remove comments and extra whitespace
        field_def = re.sub(r'--.*$', '', field_def, flags=re.MULTILINE).strip()
        if not field_def:
            return None

        # Extract field name (first word)
        parts = field_def.split(None, 1)
        if len(parts) < 2:
            return None

        field_name = parts[0].strip()
        type_and_constraints = parts[1].strip()

        # Check if nullable
        nullable = 'NOT NULL' not in type_and_constraints.upper()

        # Parse the data type
        spark_type = self._parse_data_type(type_and_constraints)

        return StructField(field_name, spark_type, nullable)

    def _parse_data_type(self, type_def: str):
        """Parse data type including complex nested types"""
        type_def = type_def.strip()

        # Handle ARRAY types
        if type_def.upper().startswith('ARRAY<'):
            inner_match = re.match(r'ARRAY<(.+)>', type_def, re.IGNORECASE | re.DOTALL)
            if inner_match:
                inner_type = self._parse_data_type(inner_match.group(1))
                return ArrayType(inner_type, True)

        # Handle STRUCT types
        if type_def.upper().startswith('STRUCT<'):
            struct_match = re.match(r'STRUCT<(.+)>', type_def, re.IGNORECASE | re.DOTALL)
            if struct_match:
                struct_fields_str = struct_match.group(1)
                struct_fields = []
                field_defs = self._parse_field_definitions(struct_fields_str)
                for field_def in field_defs:
                    if ':' in field_def:
                        name_type = field_def.split(':', 1)
                        if len(name_type) == 2:
                            field_name = name_type[0].strip()
                            field_type = self._parse_data_type(name_type[1].strip())
                            struct_fields.append(StructField(field_name, field_type, True))
                return StructType(struct_fields)

        # Handle basic types
        return self._map_sql_type_to_spark(type_def)

    def _map_sql_type_to_spark(self, sql_type: str):
        return SparkJDBCMapper.map_sql_type_to_spark(sql_type)
    
    def _map_spark_to_sql_type(self, spark_type):
        return SparkJDBCMapper.map_spark_to_sql_type(spark_type)

    def convert_jdbc_to_ddl_types(self, df: DataFrame, ddl_schema: StructType) -> DataFrame:
        return SparkJDBCMapper.convert_jdbc_to_ddl_types(df, ddl_schema)

    def convert_ddl_to_jdbc_types(self, df: DataFrame) -> DataFrame:
        return SparkJDBCMapper.convert_ddl_to_jdbc_types(df)
