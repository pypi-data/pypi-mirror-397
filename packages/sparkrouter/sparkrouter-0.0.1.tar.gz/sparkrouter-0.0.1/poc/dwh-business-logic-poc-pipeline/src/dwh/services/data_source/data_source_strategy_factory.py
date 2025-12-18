from typing import Dict, Any

from pyspark.sql import SparkSession

from dwh.services.data_source.data_source_strategy import DataSourceStrategy
from dwh.services.data_source.delta_data_source_strategy import DeltaDataSourceStrategy
from dwh.services.data_source.jdbc_data_source_strategy import JDBCDataSourceStrategy
from dwh.services.data_source.json_lines_data_source_strategy import JsonLinesDataSourceStrategy
from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
from dwh.services.schema.schema_service import SchemaService


class DataSourceStrategyFactory:

    # valid_types = ['SPARK', 'JDBC', 'DATABRICKS', 'PARQUET', 'DELTA']
    valid_types = ['JDBC', 'PARQUET', 'DELTA', 'JSONL']

    @staticmethod
    def _get_service_type(config: Dict[str, str]) -> str:
        type = config.get('strategy')
        if not type:
            raise ValueError(f"Missing strategy. Valid options are: {', '.join(DataSourceStrategyFactory.valid_types)}")
        type = type.strip().upper()
        return type

    @staticmethod
    def create_data_source_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> DataSourceStrategy:
        print("DataSourceStrategy Configuration:", config)

        strategy = DataSourceStrategyFactory._get_service_type(config=config)
        if strategy == 'DELTA':
            return DeltaDataSourceStrategy(
                spark=spark,
                schema_service=schema_service,
                path=config['path']
            )
        elif strategy == 'JDBC' or strategy == 'POSTGRES':
            return DataSourceStrategyFactory._jdbc_strategy(spark, schema_service, config)
        elif strategy == 'PARQUET':
            return DataSourceStrategyFactory._parquet_strategy(spark, schema_service, config)
        elif strategy == 'JSONL':
            return DataSourceStrategyFactory._json_lines_strategy(spark, schema_service, config)
        else:
            raise ValueError(f"Unsupported strategy[{type}]. Valid options are: {', '.join(DataSourceStrategyFactory.valid_types)}")

    @staticmethod
    def _parquet_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> ParquetDataSourceStrategy:
        path = config['path']
        recursive = config.get('recursive', False)
        return ParquetDataSourceStrategy(
            spark=spark,
            schema_service=schema_service,
            path=path,
            recursive=recursive
        )

    @staticmethod
    def _jdbc_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> JDBCDataSourceStrategy:
        jdbc_url = config.get('jdbc_url')
        properties = config.get('properties')
        return JDBCDataSourceStrategy(
            spark=spark,
            schema_service=schema_service,
            jdbc_url=jdbc_url,
            properties=properties
        )

    @staticmethod
    def _json_lines_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> JsonLinesDataSourceStrategy:
        path = config['path']
        recursive = config.get('recursive', False)
        return JsonLinesDataSourceStrategy(
            spark=spark,
            schema_service=schema_service,
            path=path,
            recursive=recursive
        )
