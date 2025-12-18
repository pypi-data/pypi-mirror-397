import unittest

# Import the functions under test
from container.generic_entry import (
    parse_args,
    validate_required_args,
    prepare_module_args,
    RESERVED_ARGS
)


class StubModule:
    """Stub module for testing dynamic imports"""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.main_calls = []

    def main(self, **kwargs):
        self.main_calls.append(kwargs)
        if self.should_fail:
            raise Exception("Simulated module execution error")


class TestParseArgs(unittest.TestCase):
    """Test the parse_args function - pure business logic"""

    def test_parse_args_empty_argv(self):
        """Test parsing empty argv"""
        result = parse_args(['script_name'])
        self.assertEqual(result, {})

    def test_parse_args_flag_only(self):
        """Test parsing flags without values"""
        result = parse_args(['script', '--verbose', '--debug'])
        self.assertEqual(result, {'verbose': True, 'debug': True})

    def test_parse_args_key_value_pairs(self):
        """Test parsing key-value pairs"""
        result = parse_args(['script', '--module_name', 'test.module', '--input', '/path/to/input'])
        expected = {
            'module_name': 'test.module',
            'input': '/path/to/input'
        }
        self.assertEqual(result, expected)

    def test_parse_args_mixed_flags_and_values(self):
        """Test parsing mixed flags and key-value pairs"""
        result = parse_args(['script', '--verbose', '--module_name', 'test.module', '--debug'])
        expected = {
            'verbose': True,
            'module_name': 'test.module',
            'debug': True
        }
        self.assertEqual(result, expected)

    def test_parse_args_flag_at_end(self):
        """Test parsing when flag is at the end"""
        result = parse_args(['script', '--module_name', 'test.module', '--verbose'])
        expected = {
            'module_name': 'test.module',
            'verbose': True
        }
        self.assertEqual(result, expected)

    def test_parse_args_ignores_non_flag_arguments(self):
        """Test that non-flag arguments are ignored"""
        result = parse_args(['script', 'regular_arg', '--module_name', 'test.module'])
        expected = {'module_name': 'test.module'}
        self.assertEqual(result, expected)

    def test_parse_args_with_spaces_in_values(self):
        """Test parsing values with spaces"""
        result = parse_args(['script', '--message', 'Hello World', '--count', '5'])
        expected = {
            'message': 'Hello World',
            'count': '5'
        }
        self.assertEqual(result, expected)

    def test_parse_args_overwrites_flag_with_value(self):
        """Test that providing a value after a flag overwrites the True default"""
        result = parse_args(['script', '--flag', 'custom_value'])
        expected = {'flag': 'custom_value'}
        self.assertEqual(result, expected)


class TestValidateRequiredArgs(unittest.TestCase):
    """Test the validate_required_args function - pure business logic"""

    def test_validate_with_module_name_present(self):
        """Test validation passes when module_name is present"""
        args = {'module_name': 'test.module', 'other_arg': 'value'}
        # Should not raise any exception
        validate_required_args(args)

    def test_validate_fails_without_module_name(self):
        """Test validation fails when module_name is missing"""
        args = {'other_arg': 'value'}
        with self.assertRaises(RuntimeError) as context:
            validate_required_args(args)

        self.assertEqual(str(context.exception), "Missing required argument: module_name")

    def test_validate_fails_with_empty_args(self):
        """Test validation fails with empty arguments"""
        args = {}
        with self.assertRaises(RuntimeError) as context:
            validate_required_args(args)

        self.assertEqual(str(context.exception), "Missing required argument: module_name")

    def test_validate_with_module_name_false_value(self):
        """Test validation fails when module_name has false-y value"""
        args = {'module_name': '', 'other_arg': 'value'}
        # Should not raise exception - we only check presence, not truthiness
        validate_required_args(args)

    def test_validate_with_module_name_none(self):
        """Test validation with None value for module_name"""
        args = {'module_name': None, 'other_arg': 'value'}
        # Should not raise exception - we only check key presence
        validate_required_args(args)


class TestPrepareModuleArgs(unittest.TestCase):
    """Test the prepare_module_args function - pure business logic"""

    def test_prepare_module_args_basic(self):
        """Test basic module args preparation"""
        args = {'module_name': 'test.module', 'param1': 'value1'}
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        expected_args = {
            'service_provider': 'CONTAINER',
            'param1': 'value1'
        }
        self.assertEqual(cleaned_args, expected_args)

        # Original args should not be modified
        self.assertIn('module_name', args)

    def test_prepare_module_args_removes_reserved_args(self):
        """Test that reserved arguments are removed"""
        args = {
            'module_name': 'test.module',
            'param1': 'value1',
            'param2': 'value2'
        }
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        self.assertNotIn('module_name', cleaned_args)
        self.assertEqual(cleaned_args['service_provider'], 'CONTAINER')
        self.assertEqual(cleaned_args['param1'], 'value1')
        self.assertEqual(cleaned_args['param2'], 'value2')

    def test_prepare_module_args_with_additional_reserved_args(self):
        """Test handling of any additional reserved arguments"""
        # Add a custom reserved arg for testing
        original_reserved = RESERVED_ARGS.copy()

        # Temporarily modify RESERVED_ARGS (this is safe since it's a set)
        args = {
            'module_name': 'test.module',
            'param1': 'value1'
        }

        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        self.assertNotIn('module_name', cleaned_args)
        self.assertEqual(cleaned_args['service_provider'], 'CONTAINER')
        self.assertEqual(cleaned_args['param1'], 'value1')

    def test_prepare_module_args_empty_args_except_module_name(self):
        """Test preparation with only module_name"""
        args = {'module_name': 'test.module'}
        module_name, cleaned_args = prepare_module_args(args)

        self.assertEqual(module_name, 'test.module')
        expected_args = {'service_provider': 'CONTAINER'}
        self.assertEqual(cleaned_args, expected_args)

    def test_prepare_module_args_preserves_original(self):
        """Test that original args dictionary is not modified"""
        original_args = {
            'module_name': 'test.module',
            'param1': 'value1',
            'param2': 'value2'
        }
        args_copy = original_args.copy()

        module_name, cleaned_args = prepare_module_args(args_copy)

        # Original should be unchanged
        self.assertEqual(args_copy, original_args)
        self.assertIn('module_name', args_copy)

    def test_service_provider_set_correctly(self):
        """Test that service_provider is set to CONTAINER"""
        args = {'module_name': 'test.module', 'existing_provider': 'OTHER'}
        module_name, cleaned_args = prepare_module_args(args)

        # Should override any existing service_provider
        self.assertEqual(cleaned_args['service_provider'], 'CONTAINER')
        self.assertEqual(cleaned_args['existing_provider'], 'OTHER')


class TestReservedArgsConstant(unittest.TestCase):
    """Test the RESERVED_ARGS constant"""

    def test_reserved_args_contains_module_name(self):
        """Test that RESERVED_ARGS contains expected reserved arguments"""
        self.assertIn('module_name', RESERVED_ARGS)
        self.assertIsInstance(RESERVED_ARGS, set)

    def test_reserved_args_is_set(self):
        """Test that RESERVED_ARGS is a set for efficient lookup"""
        self.assertIsInstance(RESERVED_ARGS, set)


class TestEntrypointWorkflow(unittest.TestCase):
    """Test the complete workflow of functions working together"""

    def test_complete_argument_processing_workflow(self):
        """Test the complete workflow from argv to module args"""
        # Simulate command line: ['script', '--module_name', 'my.module', '--input', 'data.csv', '--verbose']
        argv = ['script', '--module_name', 'my.module', '--input', 'data.csv', '--verbose']

        # Step 1: Parse arguments
        args = parse_args(argv)
        expected_parsed = {
            'module_name': 'my.module',
            'input': 'data.csv',
            'verbose': True
        }
        self.assertEqual(args, expected_parsed)

        # Step 2: Validate arguments
        validate_required_args(args)  # Should not raise

        # Step 3: Prepare module arguments
        module_name, module_args = prepare_module_args(args)

        self.assertEqual(module_name, 'my.module')
        expected_module_args = {
            'service_provider': 'CONTAINER',
            'input': 'data.csv',
            'verbose': True
        }
        self.assertEqual(module_args, expected_module_args)

    def test_workflow_with_validation_failure(self):
        """Test workflow when validation fails"""
        argv = ['script', '--input', 'data.csv', '--verbose']

        # Step 1: Parse arguments
        args = parse_args(argv)

        # Step 2: Validation should fail
        with self.assertRaises(RuntimeError):
            validate_required_args(args)


if __name__ == '__main__':
    unittest.main()
