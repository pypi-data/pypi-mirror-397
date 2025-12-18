"""Test strategy implementations for functional testing"""
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.data.data_serializer import DataSerializer
from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
from dwh.services.data_sink.delta_data_sink_strategy import DeltaDataSinkStrategy
from dwh.services.data_sink.parquet_data_sink_strategy import ParquetDataSinkStrategy
from dwh.services.data_sink.jdbc_data_sink_strategy import JDBCDataSinkStrategy


class FunctionalTestDataSourceStrategy(ParquetDataSourceStrategy):
    """Source strategy that provides initial test data from PromotionDataBuilder"""
    
    def __init__(self, spark, schema_service, path, builder: PromotionDataBuilder, recursive=False, debug_schemas=False):
        super().__init__(spark, schema_service, path, recursive, debug_schemas)
        self.builder = builder
    
    def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
        """Override only backend I/O - return test data matching expected schema structure"""
        return DataSerializer.to_dataframe(self.builder, self.spark)


class FunctionalValidationDataSourceStrategy(ParquetDataSourceStrategy):
    """Source strategy that reads data written by sink strategies for DQ validation"""
    
    def __init__(self, spark, schema_service, path, sink_strategy, recursive=False, debug_schemas=False):
        super().__init__(spark, schema_service, path, recursive, debug_schemas)
        self.sink_strategy = sink_strategy  # Reference to sink that wrote the data
    
    def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
        """Override to return the data that was written by the sink strategy"""
        if hasattr(self.sink_strategy, 'written_data') and self.sink_strategy.written_data:
            return self.spark.createDataFrame(self.sink_strategy.written_data, required_schema)
        else:
            return self.spark.createDataFrame([], required_schema)
    



class FunctionalDeltaDataSinkStrategy(DeltaDataSinkStrategy):
    """Test implementation extending DeltaDataSinkStrategy for functional testing"""
    
    def __init__(self, spark, schema_service, path, recursive=False, debug_schemas=False):
        super().__init__(spark, schema_service, path, debug_schemas)
        self.written_data = []
    
    def _write_delta_file(self, df: DataFrame, full_path: str, mode: str) -> None:
        """Override only backend I/O - simulate Delta write while preserving business logic"""
        self.written_data = df.collect()
        print(f"TEST DELTA SINK: Simulated write of {len(self.written_data)} rows to {full_path}")


class FunctionalParquetDataSinkStrategy(ParquetDataSinkStrategy):
    """Test implementation extending ParquetDataSinkStrategy for functional testing"""
    
    def __init__(self, spark, schema_service, path, debug_schemas=False):
        super().__init__(spark, schema_service, path, debug_schemas)
        self.written_data = []
    
    def _write_parquet_file(self, df: DataFrame, full_path: str, mode: str) -> None:
        """Override only backend I/O - simulate Parquet write while preserving business logic"""
        self.written_data = df.collect()
        print(f"TEST PARQUET SINK: Simulated write of {len(self.written_data)} rows to {full_path}")


class FunctionalJDBCDataSinkStrategy(JDBCDataSinkStrategy):
    """Test implementation extending JDBCDataSinkStrategy for functional testing"""
    
    def __init__(self, spark, schema_service, jdbc_url, properties, debug_schemas=False):
        super().__init__(spark, schema_service, jdbc_url, properties, debug_schemas)
        self.written_data = []
        self.executed_sql = []
        self.stage_data_source = None  # Will be set to simulate COPY from stage
    
    def set_stage_data_source(self, stage_sink_strategy):
        """Set reference to stage data for COPY simulation"""
        self.stage_data_source = stage_sink_strategy
    
    def _write_dataframe(self, df: DataFrame, sink_table: str) -> None:
        """Override abstract method - simulate JDBC write"""
        self.written_data = df.collect()
        print(f"TEST JDBC SINK: Simulated write of {len(self.written_data)} rows to {sink_table}")
    
    def get_type(self) -> str:
        """Override abstract method - return strategy type"""
        return "JDBC_TEST"
    
    def execute_sql(self, sql: str) -> None:
        """Override only backend I/O - simulate SQL execution while preserving business logic"""
        self.executed_sql.append(sql)
        
        print(f"DEBUG JDBC: Executing SQL: {sql[:100]}...")
        
        # Simulate COPY operation by copying data from stage to Redshift
        if 'COPY' in sql.upper():
            print(f"DEBUG JDBC: Detected COPY operation")
            print(f"DEBUG JDBC: stage_data_source exists: {self.stage_data_source is not None}")
            if self.stage_data_source:
                print(f"DEBUG JDBC: stage_data_source has written_data: {hasattr(self.stage_data_source, 'written_data')}")
                if hasattr(self.stage_data_source, 'written_data'):
                    print(f"DEBUG JDBC: Stage data count: {len(self.stage_data_source.written_data)}")
            
            if self.stage_data_source and hasattr(self.stage_data_source, 'written_data'):
                # Simulate COPY by copying stage data to Redshift
                stage_data = self.stage_data_source.written_data.copy()
                # Add etl_created_at timestamp to simulate the data being "copied" to Redshift
                from datetime import datetime
                current_time = datetime.now()
                print(f"DEBUG JDBC: Adding etl_created_at timestamp: {current_time}")
                
                for row_dict in stage_data:
                    if hasattr(row_dict, 'asDict'):
                        row_data = row_dict.asDict()
                    else:
                        row_data = dict(row_dict)
                    row_data['etl_created_at'] = current_time
                
                self.written_data = stage_data
                print(f"DEBUG JDBC COPY: Simulated COPY of {len(self.written_data)} rows from stage to Redshift")
            else:
                print(f"DEBUG JDBC: COPY simulation failed - no stage data available")
        
