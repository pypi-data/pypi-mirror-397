import json
import subprocess
import pytest
import tempfile
import os
from datetime import datetime

from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.data.pyarrow_data_serializer import PyArrowDataSerializer
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema

pytestmark = pytest.mark.integration


class TestLoadPromosJobIntegrationNew:
    """Integration tests for LoadPromosJob"""
    
    @pytest.fixture(autouse=True)
    def setup_bucket(self, s3_client):
        """Setup clean S3 bucket for each test"""
        bucket = "test-data"
        
        # Skip cleanup if preserving files for debugging
        if not os.environ.get('PRESERVE_S3_FILES'):
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket)
                if 'Contents' in objects:
                    delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
                    s3_client.delete_objects(Bucket=bucket, Delete={'Objects': delete_keys})
                s3_client.delete_bucket(Bucket=bucket)
            except:
                pass
            
        try:
            s3_client.create_bucket(Bucket=bucket)
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            pass
        
        # Docker-compose handles schema setup via minio-setup service
        
        yield
        
        # Preserve files if requested, even on test failure
        if os.environ.get('PRESERVE_S3_FILES'):
            print("\nDEBUG: Preserving S3 files for inspection")
            self._debug_s3_contents(s3_client)
        
    @pytest.fixture(autouse=True)
    def setup_database(self, clean_database, test_ddl_file_reader):
        """Setup clean database with required schemas and tables for each test"""
        conn = clean_database
        
        ddl_files = [
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
        ]
        
        for ddl_file in ddl_files:
            sql = test_ddl_file_reader.read_ddl_file(ddl_file)
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    def _stage_data(self, test_data_builder: PromotionDataBuilder, s3_client):
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            PyArrowDataSerializer.to_parquet(test_data_builder, temp_file_path)
            bucket = "test-data"
            key = "dl_base/ecom_sflycompromotion_promotions/data.parquet"
            
            with open(temp_file_path, 'rb') as f:
                s3_client.put_object(Bucket=bucket, Key=key, Body=f.read())

            return f"s3a://{bucket}/{key}"
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_load_promos_job(self, schema_service, s3_client, clean_database):
        # Use exact same parameters as functional test
        start_date = "2023-11-01"
        end_date = "2023-11-30"
        created_by = "functional_test_user"
        
        # Create test data using default dates from PromotionDataBuilder (same as functional test)
        test_data_builder = (PromotionDataBuilder(schema_service)
                             .with_id("PROMO_TEST_001")
                             .with_name("Business Logic Test Promotion")
                             .with_promotion_type("PERCENTAGE_DISCOUNT")
                             .with_tags("BLACK_FRIDAY", "ELECTRONICS", "SEASONAL", "HIGH_VALUE"))
        
        # Do NOT modify the default dates - use exactly what functional test uses
        s3_path = self._stage_data(test_data_builder, s3_client)
        print(f"DEBUG: Test data staged to {s3_path}")
        print(f"DEBUG: Test data ptn_ingress_date: {test_data_builder.records[0]['ptn_ingress_date']}")
        print(f"DEBUG: Test data updatedate: {test_data_builder.records[0]['updatedate']}")
        print(f"DEBUG: Date range: {start_date} to {end_date}")

        cmd = [
            "docker-compose", "-f", "docker/docker-compose.yml", "run", "--rm",
            "spark-submit",
            "--module_name", "dwh.jobs.load_promos.load_promos_job_factory",
            "--load_promos_job", json.dumps({
                "job_failed_notifications": {"notification_service": "NOOP"},
                "job_success_notifications": {"notification_service": "NOOP"},
                "data_quality_notifications": {"notification_service": "NOOP"},
                "extractor_config": {"strategy": "PARQUET", "source_table": s3_path},
                "unity_loader_config": {"strategy": "DELTA", "path": "s3a://test-data/unity-catalog/promotions/d_promotion_3_0/"},
                "stage_loader_config": {"strategy": "PARQUET", "path": "s3a://test-data/staging/promotions/"},
                "redshift_loader_config": {
                    "strategy": "POSTGRES",
                    "jdbc_url": "jdbc:postgresql://postgres:5432/postgres_db",
                    "properties": {"user": "postgres_user", "password": "postgres_password", "driver": "org.postgresql.Driver"}
                },
                "schema_service": {
                    "ddl_reader": "S3",
                    "region": "us-east-1",
                    "bucket": "code-bucket",
                    "prefix": "",
                    "endpoint_url": "http://minio:9000",
                    "aws_access_key_id": "minioadmin",
                    "aws_secret_access_key": "minioadmin"
                }
            }),
            "--start_date", start_date,
            "--end_date", end_date,
            "--created_by", created_by
        ]

        process = subprocess.run(cmd, capture_output=True, text=True)
        print(f"STDOUT:\n{process.stdout}")
        print(f"STDERR:\n{process.stderr}")
        print(f"DEBUG: process.returncode = {process.returncode} (type: {type(process.returncode)})")
        # Always show S3 contents for debugging
        self._debug_s3_contents(s3_client)
        
        assert process.returncode == 0, f"Command failed with return code {process.returncode}: {process.stderr}"
        
        self._validate_data_loaded(clean_database, test_data_builder, s3_client)
    
    def _validate_data_loaded(self, conn, expected_data_builder: PromotionDataBuilder, s3_client):
        """Validate data was loaded correctly to both S3 staging and database core table"""
        # Validate S3 staging parquet files
        print("DEBUG: Validating S3 staging parquet files")
        self._validate_s3_staging_data(expected_data_builder, s3_client)
        
        # Validate database core table
        with conn.cursor() as cur:
            print(f"DEBUG: Validating {LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME}")
            self._validate_complete_table(cur, LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME, expected_data_builder)

    def _validate_complete_table(self, cur, table_name: str, expected_data: PromotionDataBuilder):
        """Validate complete table schema and all field values"""
        schema_name = table_name.split('.')[0]
        table_only = table_name.split('.')[1]
        
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table_only}' 
            AND table_schema = '{schema_name}'
            ORDER BY ordinal_position
        """)
        schema_columns = {row[0]: {'type': row[1], 'nullable': row[2]} for row in cur.fetchall()}
        assert len(schema_columns) > 0, f"Table {table_name} doesn't exist"

        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        assert len(rows) == 1, f"Expected 1 record in {table_name}, got {len(rows)}"

        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name.split('.')[1]}' AND table_schema = '{table_name.split('.')[0]}' ORDER BY ordinal_position")
        column_names = [row[0] for row in cur.fetchall()]
        data_row = dict(zip(column_names, rows[0]))
        expected_record = expected_data.records[0]

        # Validate ALL columns exist and have correct values
        for col_name, col_info in schema_columns.items():
            assert col_name in data_row, f"Column {col_name} missing from data"
            actual_value = data_row[col_name]
            
            # Validate specific expected values using PromotionDataBuilder field names
            if col_name == 'promotionid':
                assert actual_value == expected_record['_id'], f"{col_name}: expected {expected_record['_id']}, got {actual_value}"
            elif col_name == 'promotioncode':
                assert actual_value == expected_record['name'], f"{col_name}: expected {expected_record['name']}, got {actual_value}"
            elif col_name == 'promotiontype':
                assert actual_value == expected_record['properties_promotionType'], f"{col_name}: expected {expected_record['properties_promotionType']}, got {actual_value}"
            elif col_name == 'tags':
                expected_tags = '|'.join(expected_record['tags'])
                assert actual_value == expected_tags, f"{col_name}: expected {expected_tags}, got {actual_value}"
            elif col_name == 'etl_created_by':
                assert actual_value == 'functional_test_user', f"{col_name}: expected functional_test_user, got {actual_value}"
            elif col_name == 'promotionstartdate':
                assert actual_value == expected_record['schedule_startDate'], f"{col_name}: expected {expected_record['schedule_startDate']}, got {actual_value}"
            elif col_name == 'promotionenddate':
                assert actual_value == expected_record['schedule_endDate'], f"{col_name}: expected {expected_record['schedule_endDate']}, got {actual_value}"
            elif col_name == 'eventupdtime':
                assert actual_value == expected_record['updatedate'], f"{col_name}: expected {expected_record['updatedate']}, got {actual_value}"
            elif col_name == 'ptn_ingress_date':
                assert actual_value == expected_record['ptn_ingress_date'], f"{col_name}: expected {expected_record['ptn_ingress_date']}, got {actual_value}"
            
            # Validate nullable constraints
            if col_info['nullable'] == 'NO' and col_name != 'etl_created_at':
                assert actual_value is not None, f"{col_name} cannot be null"
        
        print(f"✓ {table_name}: All {len(schema_columns)} columns fully validated")
    
    def _validate_s3_staging_data(self, expected_data_builder: PromotionDataBuilder, s3_client):
        """Validate S3 staging parquet files contain expected data"""
        import pyarrow.parquet as pq
        import pyarrow as pa
        
        bucket = "test-data"
        prefix = "staging/promotions/"
        
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response:
            raise AssertionError(f"No staging files found at s3a://{bucket}/{prefix}")
        
        parquet_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.parquet')]
        if not parquet_files:
            raise AssertionError(f"No parquet files found in staging path s3a://{bucket}/{prefix}")
        
        # Validate ALL parquet files
        total_records = 0
        expected_record = expected_data_builder.records[0]
        
        for file_key in parquet_files:
            file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
            table = pq.read_table(pa.BufferReader(file_obj['Body'].read()))
            df = table.to_pandas()
            total_records += len(df)
            
            print(f"DEBUG: Staging file {file_key} columns: {list(df.columns)}")
            
            # Validate ALL records in this file
            for idx, row in df.iterrows():
                # Map staging column names to expected values from PromotionDataBuilder
                field_mappings = {
                    'promotionid': expected_record['_id'],
                    'promotioncode': expected_record['name'],
                    'promotiontype': expected_record['properties_promotionType'],
                    'promotionstartdate': expected_record['schedule_startDate'],
                    'promotionenddate': expected_record['schedule_endDate'],
                    'eventupdtime': expected_record['updatedate'],
                    'etl_created_by': 'functional_test_user'
                }
                
                # Validate mapped fields
                for staging_col, expected_val in field_mappings.items():
                    if staging_col in df.columns:
                        actual_val = row[staging_col]
                        assert actual_val == expected_val, f"File {file_key} row {idx}: {staging_col} expected {expected_val}, got {actual_val}"
                
                # Validate tags (pipe-separated string)
                if 'tags' in df.columns and row['tags'] is not None:
                    expected_tags = '|'.join(expected_record['tags'])
                    assert row['tags'] == expected_tags, f"File {file_key} row {idx}: tags expected {expected_tags}, got {row['tags']}"
                
                # Validate all critical fields are not null
                critical_fields = ['promotionid', 'promotiontype', 'etl_created_by']
                for field in critical_fields:
                    if field in df.columns:
                        assert row[field] is not None, f"File {file_key} row {idx}: {field} is unexpectedly null"
        
        assert total_records == 1, f"Expected 1 total record across all staging files, got {total_records}"
        print(f"✓ S3 staging data: All {len(parquet_files)} files and {total_records} records fully validated")
    
    def _debug_s3_contents(self, s3_client):
        """Debug helper to show all S3 contents"""
        try:
            response = s3_client.list_objects_v2(Bucket="test-data")
            if 'Contents' in response:
                print("\nDEBUG: S3 Contents:")
                for obj in response['Contents']:
                    print(f"  {obj['Key']} ({obj['Size']} bytes)")
            else:
                print("\nDEBUG: No files found in S3 bucket")
        except Exception as e:
            print(f"\nDEBUG: Error listing S3 contents: {e}")