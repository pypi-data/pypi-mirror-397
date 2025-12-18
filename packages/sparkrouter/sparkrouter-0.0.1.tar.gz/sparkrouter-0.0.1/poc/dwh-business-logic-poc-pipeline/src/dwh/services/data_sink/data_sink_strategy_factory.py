from typing import Dict, Any

from pyspark.sql import SparkSession

from dwh.services.data_sink.data_sink_strategy import DataSinkStrategy
from dwh.services.data_sink.delta_data_sink_strategy import DeltaDataSinkStrategy
from dwh.services.data_sink.json_lines_data_sink_strategy import JsonLinesDataSinkStrategy
from dwh.services.data_sink.parquet_data_sink_strategy import ParquetDataSinkStrategy
from dwh.services.data_sink.postgres_data_sink_strategy import PostgresDataSinkStrategy
from dwh.services.data_sink.redshift_data_sink_strategy import RedshiftDataSinkStrategy
from dwh.services.schema.schema_service import SchemaService


class DataSinkStrategyFactory:

    valid_types = ['DELTA', 'PARQUET', 'REDSHIFT', 'POSTGRES', 'JSONL']

    @staticmethod
    def _get_service_type(config: Dict[str, str]) -> str:
        type = config.get('strategy')
        if not type:
            raise ValueError(f"Missing strategy. Valid options are: {', '.join(DataSinkStrategyFactory.valid_types)}")
        type = type.strip().upper()
        return type

    @staticmethod
    def create_data_sink_strategy(spark: SparkSession, schema_service: SchemaService, config: Dict[str, Any]) -> DataSinkStrategy:
        print("DataSinkStrategy Configuration:", config)

        strategy = DataSinkStrategyFactory._get_service_type(config=config)
        if strategy == 'DELTA':
            return DeltaDataSinkStrategy(
                spark=spark,
                schema_service=schema_service,
                path=config['path'],
                debug_schemas=config.get('debug_schemas', False)
            )
        elif strategy == 'PARQUET':
            return ParquetDataSinkStrategy(
                spark=spark,
                schema_service=schema_service,
                path=config['path'],
                debug_schemas=config.get('debug_schemas', False)
            )
        elif strategy == 'POSTGRES':
            return PostgresDataSinkStrategy(
                spark=spark,
                schema_service=schema_service,
                jdbc_url=config.get('jdbc_url'),
                properties=config.get('properties'),
                debug_schemas=config.get('debug_schemas', False)
            )
        elif strategy == 'REDSHIFT':
            return RedshiftDataSinkStrategy(
                spark=spark,
                schema_service=schema_service,
                jdbc_url=config.get('jdbc_url'),
                s3_staging_path=config.get('s3_staging_path'),
                properties=config.get('properties'),
                debug_schemas=config.get('debug_schemas', False)
            )
        elif strategy == 'JSONL':
            return JsonLinesDataSinkStrategy(
                spark=spark,
                schema_service=schema_service,
                path=config['path'],
                debug_schemas=config.get('debug_schemas', False)
            )
        else:
            raise ValueError(f"Unsupported strategy[{strategy}]. Valid options are: {', '.join(DataSinkStrategyFactory.valid_types)}")
