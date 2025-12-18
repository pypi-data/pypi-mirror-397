"""
PyArrow-based data serialization utilities for converting builder records to parquet files
"""
from typing import List, Dict, Any, Union, TYPE_CHECKING
import pyarrow as pa
import pyarrow.parquet as pq
from pyspark.sql.types import StructType
from pyspark.sql import Row
from datetime import datetime

if TYPE_CHECKING:
    from dwh.data.schema_data_builder import SchemaDataBuilder


class PyArrowDataSerializer:
    """PyArrow-based utility class for serializing data builder records to parquet format"""
    
    @staticmethod
    def _convert_spark_schema_to_pyarrow(spark_schema: StructType) -> pa.Schema:
        """Convert Spark StructType to PyArrow Schema"""
        fields = []
        for field in spark_schema.fields:
            arrow_type = PyArrowDataSerializer._convert_spark_type_to_arrow(field.dataType)
            arrow_field = pa.field(field.name, arrow_type, nullable=field.nullable)
            fields.append(arrow_field)
        return pa.schema(fields)
    
    @staticmethod
    def _convert_spark_type_to_arrow(spark_type):  # noqa: C901
        """Convert Spark DataType to PyArrow DataType"""
        from pyspark.sql.types import (
            StringType, IntegerType, LongType, DoubleType, FloatType, 
            BooleanType, TimestampType, DateType, ArrayType, StructType
        )
        
        if isinstance(spark_type, StringType):
            return pa.string()
        elif isinstance(spark_type, IntegerType):
            return pa.int32()
        elif isinstance(spark_type, LongType):
            return pa.int64()
        elif isinstance(spark_type, DoubleType):
            return pa.float64()
        elif isinstance(spark_type, FloatType):
            return pa.float32()
        elif isinstance(spark_type, BooleanType):
            return pa.bool_()
        elif isinstance(spark_type, TimestampType):
            return pa.timestamp('us')
        elif isinstance(spark_type, DateType):
            return pa.date32()
        elif isinstance(spark_type, ArrayType):
            element_type = PyArrowDataSerializer._convert_spark_type_to_arrow(spark_type.elementType)
            return pa.list_(element_type)
        elif isinstance(spark_type, StructType):
            fields = []
            for field in spark_type.fields:
                arrow_type = PyArrowDataSerializer._convert_spark_type_to_arrow(field.dataType)
                arrow_field = pa.field(field.name, arrow_type, nullable=field.nullable)
                fields.append(arrow_field)
            return pa.struct(fields)
        else:
            return pa.string()
    
    @staticmethod
    def _convert_record_values(records: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """Convert records to column-oriented format for PyArrow table creation"""
        if not records:
            return {}
        
        # Get all field names from the first record
        field_names = list(records[0].keys())
        
        # Create column-oriented data
        columns = {}
        for field_name in field_names:
            column_values = []
            for record in records:
                value = record.get(field_name)
                converted_value = PyArrowDataSerializer._convert_value(value)
                column_values.append(converted_value)
            columns[field_name] = column_values
        
        return columns
    
    @staticmethod
    def _convert_value(value: Any) -> Any:
        """Convert individual values to PyArrow-compatible format"""
        if value is None:
            return None
        elif isinstance(value, Row):
            # Convert Spark Row to dict
            return {field: PyArrowDataSerializer._convert_value(value[field]) for field in value.__fields__}
        elif isinstance(value, list):
            # Convert list elements
            return [PyArrowDataSerializer._convert_value(item) for item in value]
        elif isinstance(value, datetime):
            # Keep datetime as-is, PyArrow handles it
            return value
        elif isinstance(value, bool):
            # Handle booleans explicitly before integers
            return bool(value)
        elif isinstance(value, int):
            # Ensure integers are 32-bit to match Spark schema expectations
            return int(value) if -2147483648 <= value <= 2147483647 else value
        else:
            # Return value as-is for primitive types
            return value
    
    @staticmethod
    def to_parquet(data: Union[List[Dict[str, Any]], 'SchemaDataBuilder'], output_path: str, schema: StructType = None) -> str:
        """Write records or builder to parquet file using PyArrow"""
        # Handle builder input
        if hasattr(data, 'to_records') and hasattr(data, 'schema'):
            records = data.to_records()
            schema = data.schema
        else:
            records = data
            if schema is None:
                raise ValueError("Schema must be provided when using raw records")
        
        if not records:
            # Create empty table with schema
            arrow_schema = PyArrowDataSerializer._convert_spark_schema_to_pyarrow(schema)
            empty_table = pa.table({field.name: pa.array([], type=field.type) for field in arrow_schema}, schema=arrow_schema)
            pq.write_table(empty_table, output_path)
            return output_path
        
        # Convert records to PyArrow-compatible format
        converted_records = PyArrowDataSerializer._convert_record_values(records)
        
        # Convert Spark schema to PyArrow schema
        arrow_schema = PyArrowDataSerializer._convert_spark_schema_to_pyarrow(schema)
        
        # Filter data to only include fields that exist in schema
        schema_fields = {field.name for field in arrow_schema}
        filtered_records = {}
        for field_name in schema_fields:
            if field_name in converted_records:
                filtered_records[field_name] = converted_records[field_name]
            else:
                # Create empty array for missing fields
                filtered_records[field_name] = [None] * len(records)
        
        # Create arrays with explicit schema casting
        arrays = []
        for field in arrow_schema:
            column_data = filtered_records[field.name]
            array = pa.array(column_data, type=field.type)
            arrays.append(array)
        
        table = pa.table(arrays, schema=arrow_schema)
        
        # Write to parquet
        pq.write_table(table, output_path)
        return output_path
    
    @staticmethod
    def from_parquet(parquet_path: str) -> List[Dict[str, Any]]:
        """Load records from parquet file using PyArrow"""
        table = pq.read_table(parquet_path)
        return table.to_pylist()
