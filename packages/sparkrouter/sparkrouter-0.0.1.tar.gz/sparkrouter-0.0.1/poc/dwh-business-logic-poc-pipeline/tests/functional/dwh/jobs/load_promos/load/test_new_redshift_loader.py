import pytest
from pyspark.sql import Row
from dwh.jobs.load_promos.load.new_redshift_loader import NewRedshiftLoader, PostgresLoadStrategy, RedshiftLoadStrategy
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from functional.dwh.jobs.load_promos.test_strategies import (
    FunctionalJDBCDataSinkStrategy,
    FunctionalValidationDataSourceStrategy,
    FunctionalParquetDataSinkStrategy
)


@pytest.mark.functional
class TestNewRedshiftLoader:
    """Functional tests for NewRedshiftLoader and database load strategies"""
    
    def test_postgres_load_strategy_reads_from_staging_and_writes_to_database(self, spark_session, schema_service):
        """Test PostgresLoadStrategy reads from S3 staging and writes to database"""
        # Create test data with TIME fields that need conversion
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("POSTGRES_TEST_001")
                           .with_name("Postgres Load Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT"))
        
        records = test_data_builder.to_records()
        raw_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform raw data to sink schema format
        transformer = PromotionTransformer(schema_service, debug_schemas=True)
        transformed_df = transformer.transform(raw_df, "test_user")
        
        # Create staging sink for S3 staging area
        staging_sink = FunctionalParquetDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            debug_schemas=True
        )
        
        # Use StageLoader to write transformed data to staging
        stage_loader = StageLoader(staging_sink)
        stage_loader.load(transformed_df)
        
        # Create staging source to read from staging
        staging_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            staging_sink
        )
        
        # Create database sink
        database_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"},
            debug_schemas=True
        )
        
        # Create PostgresLoadStrategy
        postgres_strategy = PostgresLoadStrategy(database_sink, staging_source)
        
        # Create loader and execute
        loader = NewRedshiftLoader(postgres_strategy)
        loader.load()
        
        # Verify data was written to database
        assert len(database_sink.written_data) == 1
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        written_df = spark_session.createDataFrame(database_sink.written_data, expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(written_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify business logic was applied correctly
        row = database_sink.written_data[0]
        assert row['promotionid'] == "POSTGRES_TEST_001"
        assert row['promotioncode'] == "Postgres Load Test"
        assert row['dailystarttime'] == "00:00:00"
        assert row['dailyendtime'] == "23:59:59"
        
        print("✓ PostgresLoadStrategy functional test passed")
    
    def test_redshift_load_strategy_executes_copy_and_merge(self, spark_session, schema_service):
        """Test RedshiftLoadStrategy executes COPY and MERGE operations"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("REDSHIFT_TEST_001")
                           .with_name("Redshift Load Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        records = test_data_builder.to_records()
        raw_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform raw data to sink schema format
        transformer = PromotionTransformer(schema_service, debug_schemas=True)
        transformed_df = transformer.transform(raw_df, "test_user")
        
        # Create staging sink for S3 staging area
        staging_sink = FunctionalParquetDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            debug_schemas=True
        )
        
        # Use StageLoader to write transformed data to staging
        stage_loader = StageLoader(staging_sink)
        stage_loader.load(transformed_df)
        
        # Create staging source to read from staging
        staging_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            staging_sink
        )
        
        # Create database sink
        database_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:redshift://test:5439/test",
            {"user": "test", "password": "test"},
            debug_schemas=True
        )
        
        # Create RedshiftLoadStrategy
        redshift_strategy = RedshiftLoadStrategy(
            database_sink, 
            "s3a://test-bucket/staging/", 
            staging_source,
            {"iam_role": "arn:aws:iam::123456789012:role/RedshiftRole"}
        )
        
        # Create loader and execute
        loader = NewRedshiftLoader(redshift_strategy)
        loader.load()
        
        # Verify SQL operations were executed
        assert len(database_sink.executed_sql) >= 2
        
        # Verify COPY SQL was executed
        copy_sql = [sql for sql in database_sink.executed_sql if 'COPY' in sql.upper()]
        assert len(copy_sql) == 1
        assert LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME in copy_sql[0]
        assert "s3a://test-bucket/staging/" in copy_sql[0]
        assert "IAM_ROLE" in copy_sql[0]
        
        # Verify MERGE SQL was executed
        merge_sql = [sql for sql in database_sink.executed_sql if 'MERGE' in sql.upper()]
        assert len(merge_sql) == 1
        assert LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME in merge_sql[0]
        
        print("✓ RedshiftLoadStrategy functional test passed")