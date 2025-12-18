"""
JDBC Type Mapping Service

Handles fundamental type conversions between:
1. DDL types -> Spark types (for schema definition)
2. JDBC-returned types -> DDL-expected types (for data conversion)

This centralizes all database-specific type mapping logic that was previously
scattered across different components.
"""
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StructType,
    StringType, IntegerType, LongType,
    TimestampType, BooleanType, DecimalType
)


class SparkJDBCMapper:
    """
    Centralized service for mapping to and from Spark and JDBC.
    
    Handles database-specific JDBC driver type mapping quirks that cause
    mismatches between DDL specifications and actual JDBC-returned types.
    """

    @staticmethod
    def map_sql_type_to_spark(sql_type: str):
        """Map SQL data types to Spark data types"""
        # Clean up the type string
        sql_type = sql_type.split()[0].upper()  # Take first word, ignore constraints

        if 'VARCHAR' in sql_type or 'TEXT' in sql_type or 'STRING' in sql_type:
            return StringType()
        elif sql_type in ['INT', 'INTEGER']:
            return IntegerType()
        elif sql_type in ['BIGINT', 'LONG']:
            return LongType()
        elif sql_type in ['TIMESTAMP', 'DATETIME']:
            return TimestampType()
        elif sql_type == 'TIME':
            # TIME fields in Spark are handled as strings in HH:MM:SS format
            # Rationale:
            # - Spark has no native TIME type (only TimestampType, DateType)
            # - Standard practice is to use StringType with HH:MM:SS format
            # - Database drivers accept HH:MM:SS strings for TIME columns
            # - Avoids confusion between TIME (time-of-day) and TIMESTAMP (date+time)
            return StringType()
        elif sql_type in ['BOOLEAN', 'BOOL']:
            return BooleanType()
        elif 'DECIMAL' in sql_type:
            return DecimalType(10, 2)  # Default precision/scale
        else:
            return StringType()  # Default fallback

    @staticmethod
    def map_spark_to_sql_type(spark_type):
        """Map Spark data types back to SQL data types"""
        if isinstance(spark_type, StringType):
            return "VARCHAR"
        elif isinstance(spark_type, IntegerType):
            return "INT"
        elif isinstance(spark_type, LongType):
            return "BIGINT"
        elif isinstance(spark_type, TimestampType):
            return "TIMESTAMP"
        elif isinstance(spark_type, BooleanType):
            return "BOOLEAN"
        elif isinstance(spark_type, DecimalType):
            return f"DECIMAL({spark_type.precision},{spark_type.scale})"
        else:
            return "VARCHAR"  # Default fallback

    @staticmethod
    def convert_jdbc_to_ddl_types(df: DataFrame, ddl_schema: StructType) -> DataFrame:
        """
        Convert JDBC-returned DataFrame types to match DDL expectations.
        Handles database-specific JDBC driver type mapping quirks.

        POSTGRESQL TIME ISSUE:
        PostgreSQL JDBC driver returns TIME columns as TimestampType with 1970-01-01 date.
        DDL TIME fields are mapped to StringType in Spark (since Spark has no TIME type).
        This conversion extracts the time portion as HH:mm:ss string.
        """
        from pyspark.sql.types import TimestampType, StringType
        from pyspark.sql.functions import date_format

        converted_df = df

        # Create mapping of field names to expected DDL types
        ddl_field_types = {field.name: field.dataType for field in ddl_schema.fields}

        for field in df.schema.fields:
            expected_type = ddl_field_types.get(field.name)

            # PostgreSQL JDBC driver bug: TIME columns returned as TimestampType
            if (isinstance(field.dataType, TimestampType)
                    and isinstance(expected_type, StringType)):
                # This indicates a DDL TIME field (TIME -> StringType mapping)
                # Convert PostgreSQL JDBC TimestampType back to time string
                converted_df = converted_df.withColumn(
                    field.name,
                    date_format(df[field.name], "HH:mm:ss")
                )

        return converted_df

    @staticmethod
    def convert_ddl_to_jdbc_types(df: DataFrame) -> DataFrame:
        """
        Convert DDL-expected DataFrame types to JDBC-compatible types for writing.
        Handles database-specific JDBC driver write requirements.
        """
        # Currently no conversions needed - JDBC write handles DDL types correctly
        # This method provides symmetry with convert_jdbc_to_ddl_types()
        # Future database-specific write conversions would go here
        return df
