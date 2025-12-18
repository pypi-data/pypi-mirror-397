"""
Data serialization utilities for converting builder records to various formats
"""
from typing import List, Dict, Any, Union, TYPE_CHECKING
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType

if TYPE_CHECKING:
    from dwh.data.schema_data_builder import SchemaDataBuilder


class DataSerializer:
    """Utility class for serializing data builder records to various formats"""
    
    @staticmethod
    def to_dataframe(data: Union[List[Dict[str, Any]], 'SchemaDataBuilder'], spark: SparkSession, schema: StructType = None) -> DataFrame:
        """Convert records or builder to Spark DataFrame with schema validation"""
        # Handle builder input
        if hasattr(data, 'to_records') and hasattr(data, 'schema'):
            records = data.to_records()
            schema = data.schema
        else:
            records = data
            if schema is None:
                raise ValueError("Schema must be provided when using raw records")
        
        if not records:
            return spark.createDataFrame([], schema)
        
        # Create DataFrame directly with the target schema to avoid casting issues
        # This handles complex nested structures properly
        try:
            df = spark.createDataFrame(records, schema)
            return df
        except Exception as e:
            # Fallback: create without schema and let Spark infer, then validate structure
            print(f"Warning: Could not create DataFrame with target schema: {e}")
            df = spark.createDataFrame(records)
            print("Created DataFrame with inferred schema:")
            df.printSchema()
            return df
    
    @staticmethod
    def to_parquet(data: Union[List[Dict[str, Any]], 'SchemaDataBuilder'], output_path: str, spark: SparkSession, schema: StructType = None) -> str:
        """Write records or builder to parquet file"""
        df = DataSerializer.to_dataframe(data, spark, schema)
        df.coalesce(1).write.mode("overwrite").parquet(output_path)
        return output_path
    
    @staticmethod
    def from_parquet(parquet_path: str, spark: SparkSession) -> List[Dict[str, Any]]:
        """Load records from parquet file"""
        df = spark.read.parquet(parquet_path)
        return [row.asDict() for row in df.collect()]
    
    @staticmethod
    def validate_parquet(parquet_path: str, spark: SparkSession) -> Dict[str, Any]:
        """Validate existing parquet file against promotion schema"""
        df = spark.read.parquet(parquet_path)
        
        schema_violations = []
        data_violations = []
        
        required_fields = ["_id", "properties_promotionType", "schedule_startDate"]
        for field in required_fields:
            if field not in df.columns:
                schema_violations.append(f"Missing required field: {field}")
        
        if "properties_promotionType" in df.columns:
            valid_types = {"PERCENTAGE_DISCOUNT", "FIXED_DISCOUNT", "BOGO", "FREE_SHIPPING", "TIERED_DISCOUNT"}
            invalid_types = df.select("properties_promotionType").distinct().rdd.map(lambda r: r[0]).collect()
            for promo_type in invalid_types:
                if promo_type not in valid_types:
                    data_violations.append(f"Invalid promotion_type: {promo_type}")
        
        return {
            "schema_violations": schema_violations,
            "data_violations": data_violations,
            "total_records": df.count()
        }
