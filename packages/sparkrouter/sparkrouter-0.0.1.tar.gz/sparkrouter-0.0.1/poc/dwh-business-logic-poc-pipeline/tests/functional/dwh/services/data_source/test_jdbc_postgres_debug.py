"""
Temporary functional test to debug PostgreSQL JDBC type mapping issues.
"""
import pytest
from datetime import datetime
import psycopg2
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType
from pyspark.sql import Row

from dwh.services.data_source.jdbc_data_source_strategy import JDBCDataSourceStrategy
from dwh.services.schema.schema_service import DDLSchemaService


@pytest.mark.skip(reason="Debug test - not part of regular test suite")
@pytest.mark.functional
class TestJDBCPostgresDebug:
    """Debug PostgreSQL JDBC type mapping by testing actual write/read cycle"""
    
    def test_postgres_type_mapping(self, spark_session, test_ddl_file_reader):
        """Test PostgreSQL type mapping with simple test table"""
        
        # Setup database connection
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres_db",
            user="postgres_user",
            password="postgres_password"
        )
        
        # Create test table with all problematic types
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS test_types CASCADE")
            cur.execute("""
                CREATE TABLE test_types (
                    id INTEGER,
                    varchar_field VARCHAR(255),
                    timestamp_field TIMESTAMP,
                    time_field TIME,
                    boolean_field BOOLEAN
                )
            """)
        conn.commit()
        
        # Create test data
        test_schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("varchar_field", StringType(), True),
            StructField("timestamp_field", TimestampType(), True),
            StructField("time_field", StringType(), True),  # TIME as string
            StructField("boolean_field", BooleanType(), True)
        ])
        
        test_data = [
            Row(
                id=1,
                varchar_field="test_string",
                timestamp_field=datetime(2023, 11, 15, 14, 45, 0),
                time_field="14:30:00",
                boolean_field=True
            )
        ]
        
        test_df = spark_session.createDataFrame(test_data, test_schema)
        
        print("\n=== ORIGINAL TEST DATA SCHEMA ===")
        test_df.printSchema()
        test_df.show(truncate=False)
        
        # Insert test data directly via PostgreSQL
        print("\n=== INSERTING TEST DATA DIRECTLY ===")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO test_types (id, varchar_field, timestamp_field, time_field, boolean_field)
                VALUES (1, 'test_string', '2023-11-15 14:45:00', '14:30:00', true)
            """)
        conn.commit()
        print("Data inserted directly into PostgreSQL")
        
        # Direct PostgreSQL inspection
        print("\n=== POSTGRESQL STORED TYPES ===")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'test_types'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            for col_name, data_type, is_nullable in columns:
                print(f"  {col_name}: {data_type}")
        
        # Read back using our JDBC strategy
        print("\n=== READING BACK WITH JDBC STRATEGY ===")
        
        # Create a simple DDL for our test table
        test_ddl_file_reader.file_contents["test_types.ddl"] = """
CREATE TABLE test_types (
    id INTEGER,
    varchar_field VARCHAR(255),
    timestamp_field TIMESTAMP,
    time_field TIME,
    boolean_field BOOLEAN
);
        """
        
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        jdbc_source = JDBCDataSourceStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://localhost:5432/postgres_db",
            {"user": "postgres_user", "password": "postgres_password", "driver": "org.postgresql.Driver"},
            debug_schemas=True
        )
        
        try:
            read_df = jdbc_source.get_source_df("test_types.ddl", "test_types")
            print("JDBC READ SCHEMA:")
            read_df.printSchema()
            read_df.show(truncate=False)
        except Exception as e:
            print(f"JDBC READ ERROR: {e}")
            print("This shows the type mismatch issue!")
        
        # Show what we expected vs what we got
        print("\n=== EXPECTED VS ACTUAL TYPES ===")
        expected_schema = schema_service.get_schema("test_types.ddl", "test_types")
        print("Expected from DDL:")
        for field in expected_schema.fields:
            print(f"  {field.name}: {field.dataType}")
        print("\nThis test demonstrates the PostgreSQL JDBC type mapping issue!")
        
        conn.close()