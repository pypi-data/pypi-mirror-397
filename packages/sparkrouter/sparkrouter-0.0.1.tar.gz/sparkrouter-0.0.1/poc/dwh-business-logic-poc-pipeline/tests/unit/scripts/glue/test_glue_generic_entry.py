import unittest

# Import the functions under test
from glue.generic_entry import (
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
        result = parse_args(['script', '--module_name', 'test.module', '--input_path', 's3://bucket/input/'])
        expected = {
            'module_name': 'test.module',
            'input_path': 's3://bucket/input/'
        }
        self.assertEqual(result, expected)

    def test_parse_args_glue_paths(self):
        """Test parsing glue-specific paths"""
        result = parse_args(
            ['script', '--module_name', 'test.module', '--output_path', 's3://bucket/output/', '--JOB_ID', 'job-123'])
        expected = {
            'module_name': 'test.module',
            'output_path': 's3://bucket/output/',
            'JOB_ID': 'job-123'
        }
        self.assertEqual(result, expected)


class TestValidateRequiredArgs(unittest.TestCase):
    """Test the validate_required_args function - pure business logic"""

    def test_validate_with_module_name_present(self):
        """Test validation passes when module_name is present"""
        args = {'module_name': 'test.module', 'JOB_ID': 'job-123'}
        validate_required_args(args)  # Should not raise

    def test_validate_fails_without_module_name(self):
        """Test validation fails when module_name is missing"""
        args = {'JOB_ID': 'job-123'}
        with self.assertRaises(RuntimeError) as context:
            validate_required_args(args)

        self.assertEqual(str(context.exception), "Missing required argument: module_name")


class TestPrepareModuleArgs(unittest.TestCase):
    """Test the prepare_module_args function - pure business logic"""

    def test_prepare_module_args_basic(self):
        """Test basic module args preparation for Glue"""
        args = {'module_name': 'test.module', 'database_name': 'analytics'}
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        expected_args = {
            'service_provider': 'GLUE',
            'database_name': 'analytics'
        }
        self.assertEqual(cleaned_args, expected_args)

        # Original args should not be modified
        self.assertIn('module_name', args)

    def test_prepare_module_args_removes_reserved_args(self):
        """Test that reserved arguments are removed"""
        args = {
            'module_name': 'test.module',
            'input_path': 's3://bucket/input/',
            'output_path': 's3://bucket/output/'
        }
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        self.assertNotIn('module_name', cleaned_args)
        self.assertEqual(cleaned_args['service_provider'], 'GLUE')
        self.assertEqual(cleaned_args['input_path'], 's3://bucket/input/')
        self.assertEqual(cleaned_args['output_path'], 's3://bucket/output/')

    def test_prepare_module_args_removes_glue_job_ids(self):
        """Test that Glue-specific reserved arguments (JOB_ID, JOB_RUN_ID) are removed"""
        args = {
            'module_name': 'test.module',
            'JOB_ID': 'job-analytics-001',
            'JOB_RUN_ID': 'jr_abc123def456',
            'input_path': 's3://bucket/input/',
            'regular_param': 'value'
        }
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        self.assertNotIn('module_name', cleaned_args)
        self.assertNotIn('JOB_ID', cleaned_args)  # Should be removed
        self.assertNotIn('JOB_RUN_ID', cleaned_args)  # Should be removed
        self.assertEqual(cleaned_args['service_provider'], 'GLUE')
        self.assertEqual(cleaned_args['input_path'], 's3://bucket/input/')
        self.assertEqual(cleaned_args['regular_param'], 'value')

    def test_service_provider_set_to_glue(self):
        """Test that service_provider is set to GLUE"""
        args = {'module_name': 'test.module', 'existing_provider': 'OTHER'}
        module_name, cleaned_args = prepare_module_args(args)

        # Should override any existing service_provider
        self.assertEqual(cleaned_args['service_provider'], 'GLUE')
        self.assertEqual(cleaned_args['existing_provider'], 'OTHER')

    def test_prepare_module_args_with_glue_paths(self):
        """Test preparation with Glue-specific paths"""
        args = {
            'module_name': 'myproject.jobs.data_processor',
            'input_path': 's3://data-lake/input/raw/',
            'output_path': 's3://data-lake/output/processed/',
            'database_name': 'analytics_db',
            'table_name': 'processed_data'
        }
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'myproject.jobs.data_processor')
        expected_args = {
            'service_provider': 'GLUE',
            'input_path': 's3://data-lake/input/raw/',
            'output_path': 's3://data-lake/output/processed/',
            'database_name': 'analytics_db',
            'table_name': 'processed_data'
        }
        self.assertEqual(cleaned_args, expected_args)


class TestReservedArgsConstant(unittest.TestCase):
    """Test the RESERVED_ARGS constant"""

    def test_reserved_args_contains_required_args(self):
        """Test that RESERVED_ARGS contains expected reserved arguments"""
        self.assertIn('module_name', RESERVED_ARGS)
        self.assertIn('JOB_ID', RESERVED_ARGS)
        self.assertIn('JOB_RUN_ID', RESERVED_ARGS)
        self.assertIsInstance(RESERVED_ARGS, set)

    def test_reserved_args_has_glue_specific_args(self):
        """Test that Glue-specific reserved args are included"""
        # Glue automatically adds these parameters
        self.assertIn('JOB_ID', RESERVED_ARGS)
        self.assertIn('JOB_RUN_ID', RESERVED_ARGS)


class TestEntrypointWorkflow(unittest.TestCase):
    """Test the complete workflow of functions working together"""

    def test_complete_glue_workflow(self):
        """Test the complete workflow for Glue job execution"""
        # Simulate Glue command line with automatic JOB_ID and JOB_RUN_ID
        argv = [
            'script',
            '--module_name', 'myproject.jobs.data_processor',
            '--input_path', 's3://data-lake/input/raw/',
            '--output_path', 's3://data-lake/output/processed/',
            '--JOB_ID', 'data-processing-job',
            '--JOB_RUN_ID', 'jr_abc123def456',
            '--num_partitions', '20'
        ]

        # Step 1: Parse arguments
        args = parse_args(argv)
        expected_parsed = {
            'module_name': 'myproject.jobs.data_processor',
            'input_path': 's3://data-lake/input/raw/',
            'output_path': 's3://data-lake/output/processed/',
            'JOB_ID': 'data-processing-job',
            'JOB_RUN_ID': 'jr_abc123def456',
            'num_partitions': '20'
        }
        self.assertEqual(args, expected_parsed)

        # Step 2: Validate arguments
        validate_required_args(args)  # Should not raise

        # Step 3: Prepare module arguments
        module_name, module_args = prepare_module_args(args)

        self.assertEqual(module_name, 'myproject.jobs.data_processor')
        expected_module_args = {
            'service_provider': 'GLUE',
            'input_path': 's3://data-lake/input/raw/',
            'output_path': 's3://data-lake/output/processed/',
            'num_partitions': '20'
            # JOB_ID and JOB_RUN_ID should be filtered out
        }
        self.assertEqual(module_args, expected_module_args)

    def test_workflow_with_glue_catalog_operations(self):
        """Test workflow with Glue catalog operations"""
        argv = [
            'script',
            '--module_name', 'analytics.jobs.catalog_updater',
            '--database_name', 'raw_data',
            '--table_name', 'customer_events',
            '--partition_key', 'date',
            '--JOB_ID', 'catalog-update-job',
            '--JOB_RUN_ID', 'jr_xyz789abc012'
        ]

        args = parse_args(argv)
        validate_required_args(args)
        module_name, module_args = prepare_module_args(args)

        self.assertEqual(module_name, 'analytics.jobs.catalog_updater')
        expected_module_args = {
            'service_provider': 'GLUE',
            'database_name': 'raw_data',
            'table_name': 'customer_events',
            'partition_key': 'date'
            # JOB_ID and JOB_RUN_ID should be filtered out
        }
        self.assertEqual(module_args, expected_module_args)

    def test_workflow_filters_job_ids_but_keeps_other_args(self):
        """Test that JOB_ID and JOB_RUN_ID are filtered but other args are preserved"""
        argv = [
            'script',
            '--module_name', 'test.module',
            '--JOB_ID', 'should-be-removed',
            '--JOB_RUN_ID', 'should-also-be-removed',
            '--regular_param', 'should-be-kept',
            '--another_param', 'also-kept'
        ]

        args = parse_args(argv)
        validate_required_args(args)
        module_name, module_args = prepare_module_args(args)

        # JOB_ID and JOB_RUN_ID should be gone
        self.assertNotIn('JOB_ID', module_args)
        self.assertNotIn('JOB_RUN_ID', module_args)

        # Regular params should be preserved
        self.assertEqual(module_args['regular_param'], 'should-be-kept')
        self.assertEqual(module_args['another_param'], 'also-kept')
        self.assertEqual(module_args['service_provider'], 'GLUE')


if __name__ == '__main__':
    unittest.main()
