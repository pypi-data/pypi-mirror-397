import unittest
from typing import Any

from dwh.jobs.schemas.schema_upgrade_job import SchemaUpgradeJob
from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService
from dwh.services.notification.notification_service import NoopNotificationService
from dwh.services.file.file_locator import FileLocator
from unit.dwh.test_utils.file_locator import DummyFileLocator


class StubDatabaseConnectionService(JdbcConnectionService):
    """Stub implementation of SQLExecutionService for testing"""

    def __init__(self, results=None, schema_versions=None, should_raise=False, raise_message=""):
        self.results = results or []
        self.schema_versions = schema_versions or {}
        self.executed_queries = []
        self.executed_params = []
        self.should_raise = should_raise
        self.raise_message = raise_message

    def connect(self) -> Any:
        pass

    def execute_query(self, sql, params=None):
        self.executed_queries.append(sql)
        self.executed_params.append(params)

        if self.should_raise:
            raise Exception(self.raise_message)

        # Handle specific SQL patterns for testing
        if "schema_version" in sql and "ORDER BY applied_at" in sql:
            schema_name = self._extract_schema_from_sql(sql)
            if schema_name in self.schema_versions:
                return [{'version': self.schema_versions[schema_name]}]
            else:
                # Simulate table does not exist error
                raise Exception("relation \"test_schema.schema_version\" does not exist")

        if "information_schema.schemata" in sql:
            # Extract schema name from SQL and check if it exists
            import re
            match = re.search(r"schema_name = '([^']+)'", sql)
            if match:
                schema_name = match.group(1)
                if schema_name == 'existing_schema':
                    return [{'schema_name': schema_name}]
            return []  # Non-existing schema by default

        return self.results

    def _extract_schema_from_sql(self, sql):
        # Extract schema name from SQL like "SELECT version FROM {schema}.schema_version"
        import re
        match = re.search(r'FROM\s+(\w+)\.schema_version', sql, re.IGNORECASE)
        return match.group(1) if match else None

    def close(self):
        pass


class StubFileLocator(FileLocator):
    """Stub implementation of FileLocator for testing"""

    def __init__(self, files=None, file_contents=None):
        self.files = files or []
        self.file_contents = file_contents or {}

    def list_files(self, path, file_extension=None):
        return self.files

    def read_file(self, path):
        return self.file_contents.get(path, f"-- Content of {path}")


class TestUpgradeSchema(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        self.notifier = NoopNotificationService()

    def test_list_upgrade_scripts(self):
        file_locator = DummyFileLocator(files=[])
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(
            alarm_service=self.notifier,
            ddl_file_service=file_locator,
            postgres_service=jdbc_connection_service
        )

        files = [
            'ddls/dw_core/003_upgrade_dw_core_v1_1_to_v1_2.sql',
            'ddls/dw_core/dw_core_v1_0.ddl',
            'ddls/dw_core/002_upgrade_dw_core_v1_0_to_v1_1.sql',
        ]

        self.assertEqual(
            job.list_upgrade_scripts('dw_core', files, current_version=0),
            [
                'ddls/dw_core/dw_core_v1_0.ddl',
                'ddls/dw_core/002_upgrade_dw_core_v1_0_to_v1_1.sql',
                'ddls/dw_core/003_upgrade_dw_core_v1_1_to_v1_2.sql',
            ]
        )

        self.assertEqual(
            job.list_upgrade_scripts('dw_core', files, current_version=1.0),
            [
                'ddls/dw_core/002_upgrade_dw_core_v1_0_to_v1_1.sql',
                'ddls/dw_core/003_upgrade_dw_core_v1_1_to_v1_2.sql',
            ]
        )

        self.assertEqual(
            job.list_upgrade_scripts('dw_core', files, current_version=1.1),
            [
                'ddls/dw_core/003_upgrade_dw_core_v1_1_to_v1_2.sql',
            ]
        )

        self.assertEqual(
            job.list_upgrade_scripts('dw_core', files, current_version=3),
            []
        )

    def test_constructor_validation(self):
        """Test constructor parameter validation"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        # Valid construction should work
        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        self.assertIsInstance(job, SchemaUpgradeJob)

        # Invalid file_locator should raise error
        with self.assertRaises(ValueError) as context:
            SchemaUpgradeJob(self.notifier, "not_a_file_locator", jdbc_connection_service)
        self.assertIn("ddl_file_service must be an instance of FileLocator", str(context.exception))

    def test_execute_job_with_string_schemas(self):
        """Test execute_job with comma-separated string of schemas"""
        file_locator = StubFileLocator(files=['ddls/redshift/test1/test1_v1_0.ddl'])
        jdbc_connection_service = StubDatabaseConnectionService(schema_versions={'test1': 1.0, 'test2': 1.1})

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        results = job.execute_job("test1,test2")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['schema'], 'test1')
        self.assertEqual(results[1]['schema'], 'test2')

    def test_execute_job_with_list_schemas(self):
        """Test execute_job with list of schemas"""
        file_locator = StubFileLocator(files=['ddls/redshift/test1/test1_v1_0.ddl'])
        jdbc_connection_service = StubDatabaseConnectionService(schema_versions={'test1': 1.0})

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        results = job.execute_job(['test1'])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['schema'], 'test1')

    def test_execute_job_with_empty_schemas(self):
        """Test execute_job with empty schemas raises error"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        with self.assertRaises(ValueError) as context:
            job.execute_job("")
        self.assertIn("schemas must be a non-empty list", str(context.exception))

        with self.assertRaises(ValueError) as context:
            job.execute_job([])
        self.assertIn("schemas must be a non-empty list", str(context.exception))

    def test_schema_exists_true(self):
        """Test schema_exists returns True for existing schema"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        exists = job.schema_exists('existing_schema')

        self.assertTrue(exists)
        self.assertIn("information_schema.schemata", jdbc_connection_service.executed_queries[0])

    def test_schema_exists_false(self):
        """Test schema_exists returns False for non-existing schema"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        exists = job.schema_exists('non_existing_schema')

        self.assertFalse(exists)

    def test_schema_exists_with_sql_error(self):
        """Test schema_exists handles SQL errors"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService(should_raise=True,
                                                                raise_message="Database connection failed")

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        with self.assertRaises(ValueError) as context:
            job.schema_exists('test_schema')
        self.assertIn("Error checking schema existence", str(context.exception))

    def test_get_schema_version_with_existing_version(self):
        """Test get_schema_version with existing version table"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService(schema_versions={'test_schema': 1.5})

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        version = job.get_schema_version('test_schema')

        self.assertEqual(version, '1.5')

    def test_get_schema_version_with_no_table(self):
        """Test get_schema_version when schema_version table doesn't exist"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        version = job.get_schema_version('new_schema')

        self.assertEqual(version, 0.0)

    def test_get_schema_version_with_sql_error(self):
        """Test get_schema_version handles non-table-existence SQL errors"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService(should_raise=True, raise_message="Permission denied")

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        with self.assertRaises(ValueError) as context:
            job.get_schema_version('test_schema')
        self.assertIn("Error getting schema version", str(context.exception))

    def test_download_script(self):
        """Test download_script reads file content"""
        file_contents = {'path/to/script.sql': 'CREATE TABLE test (id INT);'}
        file_locator = StubFileLocator(file_contents=file_contents)
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        content = job.download_script('path/to/script.sql')

        self.assertEqual(content, 'CREATE TABLE test (id INT);')

    def test_upgrade_schema_with_no_upgrades_needed(self):
        """Test upgrade_schema when no upgrades are needed"""
        file_locator = StubFileLocator(files=[])
        jdbc_connection_service = StubDatabaseConnectionService(schema_versions={'test_schema': 1.5})

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)
        result = job.upgrade_schema('test_schema')

        self.assertEqual(result['schema'], 'test_schema')
        self.assertEqual(result['starting_version'], '1.5')
        self.assertEqual(result['upgraded_version'], '1.5')

    def test_upgrade_schema_with_upgrades_needed(self):
        """Test upgrade_schema when upgrades are needed"""
        files = ['ddls/redshift/test_schema/001_upgrade_test_schema_v1_0_to_v1_1.sql']
        file_contents = {
            'ddls/redshift/test_schema/001_upgrade_test_schema_v1_0_to_v1_1.sql': 'ALTER TABLE test ADD COLUMN new_col INT;'}
        file_locator = StubFileLocator(files=files, file_contents=file_contents)

        # Set up SQL service to return different versions before and after upgrade
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        # Mock the version check to return 1.0 initially, then 1.1 after upgrade
        def mock_get_version(schema):
            if len(jdbc_connection_service.executed_queries) < 3:  # First call
                return '1.0'
            else:  # After upgrade
                return '1.1'

        # Override the get_schema_version method for this test
        original_get_version = job.get_schema_version
        job.get_schema_version = mock_get_version

        result = job.upgrade_schema('test_schema')

        # Verify transaction commands were executed
        self.assertIn('BEGIN', jdbc_connection_service.executed_queries)
        self.assertIn('ALTER TABLE test ADD COLUMN new_col INT;', jdbc_connection_service.executed_queries)
        self.assertIn('COMMIT', jdbc_connection_service.executed_queries)

        # Restore original method
        job.get_schema_version = original_get_version

    def test_upgrade_schema_with_error_and_rollback(self):
        """Test upgrade_schema handles errors and performs rollback"""
        files = ['ddls/redshift/test_schema/001_upgrade_test_schema_v1_0_to_v1_1.sql']
        file_contents = {'ddls/redshift/test_schema/001_upgrade_test_schema_v1_0_to_v1_1.sql': 'INVALID SQL;'}
        file_locator = StubFileLocator(files=files, file_contents=file_contents)

        # SQL service that raises error on the upgrade script
        jdbc_connection_service = StubDatabaseConnectionService()
        original_execute = jdbc_connection_service.execute_query

        def mock_execute(sql, params=None):
            if 'INVALID SQL' in sql:
                raise Exception("SQL syntax error")
            return original_execute(sql, params)

        jdbc_connection_service.execute_query = mock_execute

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        # Mock version to trigger upgrade
        job.get_schema_version = lambda schema: '1.0'

        with self.assertRaises(ValueError) as context:
            job.upgrade_schema('test_schema')

        self.assertIn("Error upgrading schema test_schema", str(context.exception))

    def test_list_upgrade_scripts_with_no_create_script_for_new_schema(self):
        """Test list_upgrade_scripts raises error when no create script found for new schema"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        # No create script for version 0
        files = ['ddls/test_schema/001_upgrade_test_schema_v1_0_to_v1_1.sql']

        with self.assertRaises(ValueError) as context:
            job.list_upgrade_scripts('test_schema', files, current_version=0)
        self.assertIn("No create script found for schema test_schema", str(context.exception))

    def test_list_upgrade_scripts_with_string_current_version(self):
        """Test list_upgrade_scripts handles string current_version"""
        file_locator = StubFileLocator()
        jdbc_connection_service = StubDatabaseConnectionService()

        job = SchemaUpgradeJob(self.notifier, file_locator, jdbc_connection_service)

        files = [
            'ddls/test_schema/test_schema_v1_0.ddl',
            'ddls/test_schema/001_upgrade_test_schema_v1_0_to_v1_1.sql',
        ]

        # Pass string version instead of float
        result = job.list_upgrade_scripts('test_schema', files, current_version="1.0")

        self.assertEqual(len(result), 1)
        self.assertIn('upgrade_test_schema_v1_0_to_v1_1.sql', result[0])


if __name__ == '__main__':
    unittest.main()
