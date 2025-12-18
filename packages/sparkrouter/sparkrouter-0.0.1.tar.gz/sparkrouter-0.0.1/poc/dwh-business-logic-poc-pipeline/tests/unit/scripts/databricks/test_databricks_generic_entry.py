import unittest

# Import the functions under test
from databricks.generic_entry import (
    parse_args,
    validate_required_args,
    prepare_module_args,
    RESERVED_ARGS
)


class TestParseArgs(unittest.TestCase):
    """Test the parse_args function - pure business logic"""

    def test_parse_args_empty_argv(self):
        """Test parsing empty argv"""
        result = parse_args(['script_name'])
        self.assertEqual(result, {})

    def test_parse_args_key_value_pairs(self):
        """Test parsing key-value pairs"""
        result = parse_args(['script', '--module_name', 'test.module', '--input_path', 'dbfs:/input/'])
        expected = {
            'module_name': 'test.module',
            'input_path': 'dbfs:/input/'
        }
        self.assertEqual(result, expected)

    def test_parse_args_databricks_paths(self):
        """Test parsing databricks-specific paths"""
        result = parse_args(
            ['script', '--module_name', 'test.module', '--output_path', 'dbfs:/output/', '--cluster_id', 'cluster-123'])
        expected = {
            'module_name': 'test.module',
            'output_path': 'dbfs:/output/',
            'cluster_id': 'cluster-123'
        }
        self.assertEqual(result, expected)


class TestValidateRequiredArgs(unittest.TestCase):
    """Test the validate_required_args function - pure business logic"""

    def test_validate_with_module_name_present(self):
        """Test validation passes when module_name is present"""
        args = {'module_name': 'test.module', 'cluster_id': 'cluster-123'}
        validate_required_args(args)  # Should not raise

    def test_validate_fails_without_module_name(self):
        """Test validation fails when module_name is missing"""
        args = {'cluster_id': 'cluster-123'}
        with self.assertRaises(RuntimeError) as context:
            validate_required_args(args)

        self.assertEqual(str(context.exception), "Missing required argument: module_name")


class TestPrepareModuleArgs(unittest.TestCase):
    """Test the prepare_module_args function - pure business logic"""

    def test_prepare_module_args_basic(self):
        """Test basic module args preparation for Databricks"""
        args = {'module_name': 'test.module', 'cluster_id': 'cluster-123'}
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        expected_args = {
            'service_provider': 'DATABRICKS',
            'cluster_id': 'cluster-123'
        }
        self.assertEqual(cleaned_args, expected_args)

        # Original args should not be modified
        self.assertIn('module_name', args)

    def test_prepare_module_args_removes_reserved_args(self):
        """Test that reserved arguments are removed"""
        args = {
            'module_name': 'test.module',
            'input_path': 'dbfs:/input/',
            'output_path': 'dbfs:/output/'
        }
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        self.assertNotIn('module_name', cleaned_args)
        self.assertEqual(cleaned_args['service_provider'], 'DATABRICKS')
        self.assertEqual(cleaned_args['input_path'], 'dbfs:/input/')
        self.assertEqual(cleaned_args['output_path'], 'dbfs:/output/')

    def test_service_provider_set_to_databricks(self):
        """Test that service_provider is set to DATABRICKS"""
        args = {'module_name': 'test.module', 'existing_provider': 'OTHER'}
        module_name, cleaned_args = prepare_module_args(args)

        # Should override any existing service_provider
        self.assertEqual(cleaned_args['service_provider'], 'DATABRICKS')
        self.assertEqual(cleaned_args['existing_provider'], 'OTHER')

    def test_prepare_module_args_with_databricks_paths(self):
        """Test preparation with Databricks-specific paths"""
        args = {
            'module_name': 'myproject.jobs.data_processor',
            'input_path': 'dbfs:/input/data.parquet',
            'output_path': 'dbfs:/output/results/',
            'cluster_id': 'cluster-abc123'
        }
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'myproject.jobs.data_processor')
        expected_args = {
            'service_provider': 'DATABRICKS',
            'input_path': 'dbfs:/input/data.parquet',
            'output_path': 'dbfs:/output/results/',
            'cluster_id': 'cluster-abc123'
        }
        self.assertEqual(cleaned_args, expected_args)


class TestReservedArgsConstant(unittest.TestCase):
    """Test the RESERVED_ARGS constant"""

    def test_reserved_args_contains_module_name(self):
        """Test that RESERVED_ARGS contains expected reserved arguments"""
        self.assertIn('module_name', RESERVED_ARGS)
        self.assertIsInstance(RESERVED_ARGS, set)


class TestEntrypointWorkflow(unittest.TestCase):
    """Test the complete workflow of functions working together"""

    def test_complete_databricks_workflow(self):
        """Test the complete workflow for Databricks job execution"""
        # Simulate Databricks command line
        argv = [
            'script',
            '--module_name', 'myproject.jobs.data_processor',
            '--input_path', 'dbfs:/input/raw_data/',
            '--output_path', 'dbfs:/output/processed/',
            '--num_partitions', '10'
        ]

        # Step 1: Parse arguments
        args = parse_args(argv)
        expected_parsed = {
            'module_name': 'myproject.jobs.data_processor',
            'input_path': 'dbfs:/input/raw_data/',
            'output_path': 'dbfs:/output/processed/',
            'num_partitions': '10'
        }
        self.assertEqual(args, expected_parsed)

        # Step 2: Validate arguments
        validate_required_args(args)  # Should not raise

        # Step 3: Prepare module arguments
        module_name, module_args = prepare_module_args(args)

        self.assertEqual(module_name, 'myproject.jobs.data_processor')
        expected_module_args = {
            'service_provider': 'DATABRICKS',
            'input_path': 'dbfs:/input/raw_data/',
            'output_path': 'dbfs:/output/processed/',
            'num_partitions': '10'
        }
        self.assertEqual(module_args, expected_module_args)

    def test_workflow_with_cluster_configuration(self):
        """Test workflow with Databricks cluster configuration"""
        argv = [
            'script',
            '--module_name', 'analytics.jobs.report_generator',
            '--cluster_id', 'cluster-analytics-001',
            '--warehouse_id', 'warehouse-sql-001',
            '--debug'
        ]

        args = parse_args(argv)
        validate_required_args(args)
        module_name, module_args = prepare_module_args(args)

        self.assertEqual(module_name, 'analytics.jobs.report_generator')
        expected_module_args = {
            'service_provider': 'DATABRICKS',
            'cluster_id': 'cluster-analytics-001',
            'warehouse_id': 'warehouse-sql-001',
            'debug': True
        }
        self.assertEqual(module_args, expected_module_args)


if __name__ == '__main__':
    unittest.main()
