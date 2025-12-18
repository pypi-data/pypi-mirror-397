"""
Parquet output builder for converting data builders to parquet files
"""

from typing import List, Dict, Any, Union, TYPE_CHECKING
from dwh.data.data_serializer import DataSerializer
from dwh.data.pyarrow_data_serializer import PyArrowDataSerializer

if TYPE_CHECKING:
    from dwh.data.schema_data_builder import SchemaDataBuilder
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType


class ParquetDataBuilder:
    """Builder for generating parquet files from data builders"""
    
    @staticmethod
    def to_parquet_spark(output_path: str, data: Union['SchemaDataBuilder', List[Dict[str, Any]]], spark: 'SparkSession', schema: 'StructType' = None) -> str:
        """Convert data builder or records to parquet file using Spark"""
        return DataSerializer.to_parquet(data, output_path, spark, schema)
    
    @staticmethod
    def to_parquet_pyarrow(output_path: str, data: Union['SchemaDataBuilder', List[Dict[str, Any]]], schema: 'StructType' = None) -> str:
        """Convert data builder or records to parquet file using PyArrow"""
        return PyArrowDataSerializer.to_parquet(data, output_path, schema)
