import pytest

from dwh.services.file.file_locator import FSFileLocator
from dwh.services.file.file_locator_factory import FileLocatorFactory


class TestFileLocatorFactory:

    def test_create_os_file_locator(self):
        # Act
        result = FileLocatorFactory.create_file_locator({
            'file_service': 'FS',
            'root_path': '/test/path'
        })

        # Assert
        assert isinstance(result, FSFileLocator)

    def test_create_os_file_locator_with_defaults(self):
        # Act
        result = FileLocatorFactory.create_file_locator({
            'file_service': 'FS',
            'root_path': '/default/path'
        })

        # Assert
        assert isinstance(result, FSFileLocator)

    def test_create_s3_file_locator_missing_bucket_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="bucket_name is required for S3FileLocator"):
            FileLocatorFactory.create_file_locator({
                'file_service': 'S3',
                'region': 'us-west-2',
            })

    def test_create_file_locator_invalid_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported file locator_type\\[INVALID\\]. Valid options are: S3, FS"):
            FileLocatorFactory.create_file_locator({
                'file_service': 'INVALID',
            })

    def test_create_file_locator_none_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="Missing file locator_type. Valid options are: S3, FS"):
            FileLocatorFactory.create_file_locator({
                'file_service': None,
            })

    def test_factory_accepts_unknown_kwargs_without_error(self):
        # Test that the factory doesn't break with extra parameters
        # Act
        result = FileLocatorFactory.create_file_locator({
            'file_service': 'FS',
            'root_path': '/test/path',
            'extra_param': 'should_be_ignored',
            'another_param': 123
        })

        # Assert
        assert isinstance(result, FSFileLocator)
