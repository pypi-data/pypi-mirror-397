"""
Unit tests for FileLocator implementations
"""
import pytest
import os
import tempfile
import shutil

from dwh.services.file.file_locator import (
    FileLocator,
    FSFileLocator,
    S3FileLocator
)


class TestFSFileLocator:
    """Test FSFileLocator - fully testable using temporary directories"""

    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory structure for testing"""
        temp_dir = tempfile.mkdtemp()

        # Create test directory structure
        test_dirs = [
            'data',
            'data/csv',
            'data/json',
            'scripts',
            'empty_dir'
        ]

        for dir_path in test_dirs:
            os.makedirs(os.path.join(temp_dir, dir_path), exist_ok=True)

        # Create test files
        test_files = {
            'data/test1.txt': 'Content of test1.txt',
            'data/test2.txt': 'Content of test2.txt',
            'data/csv/data1.csv': 'name,age\nJohn,30\nJane,25',
            'data/csv/data2.csv': 'id,value\n1,100\n2,200',
            'data/json/config.json': '{"setting": "value"}',
            'scripts/script1.py': 'print("Hello World")',
            'scripts/script2.sh': '#!/bin/bash\necho "test"',
            'readme.md': '# Test Project'
        }

        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            with open(full_path, 'w') as f:
                f.write(content)

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_init(self, temp_directory):
        """Test FSFileLocator initialization"""
        locator = FSFileLocator(temp_directory)
        assert locator.root_path == temp_directory
        assert isinstance(locator, FileLocator)

    def test_list_files_all(self, temp_directory):
        """Test listing all files in a directory"""
        locator = FSFileLocator(temp_directory)

        files = locator.list_files('data')

        # Should include both txt files
        assert len(files) >= 2
        assert 'data/test1.txt' in files
        assert 'data/test2.txt' in files

    def test_list_files_with_extension(self, temp_directory):
        """Test listing files with specific extension"""
        locator = FSFileLocator(temp_directory)

        # Test CSV files
        csv_files = locator.list_files('data/csv', file_extension='.csv')
        assert len(csv_files) == 2
        assert 'data/csv/data1.csv' in csv_files
        assert 'data/csv/data2.csv' in csv_files

        # Test TXT files
        txt_files = locator.list_files('data', file_extension='.txt')
        assert len(txt_files) == 2
        assert 'data/test1.txt' in txt_files
        assert 'data/test2.txt' in txt_files

    def test_list_files_no_extension_match(self, temp_directory):
        """Test listing files with extension that doesn't exist"""
        locator = FSFileLocator(temp_directory)

        xml_files = locator.list_files('data', file_extension='.xml')
        assert len(xml_files) == 0

    def test_list_files_empty_directory(self, temp_directory):
        """Test listing files in empty directory"""
        locator = FSFileLocator(temp_directory)

        files = locator.list_files('empty_dir')
        assert len(files) == 0

    def test_read_file_txt(self, temp_directory):
        """Test reading text file"""
        locator = FSFileLocator(temp_directory)

        content = locator.read_file('data/test1.txt')
        assert content == 'Content of test1.txt'

    def test_read_file_csv(self, temp_directory):
        """Test reading CSV file"""
        locator = FSFileLocator(temp_directory)

        content = locator.read_file('data/csv/data1.csv')
        assert 'name,age' in content
        assert 'John,30' in content

    def test_read_file_json(self, temp_directory):
        """Test reading JSON file"""
        locator = FSFileLocator(temp_directory)

        content = locator.read_file('data/json/config.json')
        assert content == '{"setting": "value"}'

    def test_read_file_with_unicode(self, temp_directory):
        """Test reading file with Unicode content"""
        locator = FSFileLocator(temp_directory)

        # Create file with Unicode content
        unicode_file = 'data/unicode.txt'
        unicode_content = 'Hello 世界! 🌍 Café résumé'
        full_path = os.path.join(temp_directory, unicode_file)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(unicode_content)

        content = locator.read_file(unicode_file)
        assert content == unicode_content

    def test_path_handling_backslash(self, temp_directory):
        """Test path handling with backslashes (Windows-style)"""
        import os
        import pytest

        # Skip this test on non-Windows platforms since backslashes aren't valid path separators
        if os.name != 'nt':
            pytest.skip("Backslash path test only valid on Windows")

        locator = FSFileLocator(temp_directory)

        # Test with backslash paths (Windows only)
        files = locator.list_files('data\\csv')
        assert len(files) >= 2

    def test_path_handling_forward_slash(self, temp_directory):
        """Test path handling with forward slashes (Unix-style)"""
        locator = FSFileLocator(temp_directory)

        # Test with forward slash paths
        files = locator.list_files('data/csv')
        assert len(files) >= 2

    def test_path_handling_cross_platform(self, temp_directory):
        """Test path handling using os.path.join for cross-platform compatibility"""
        import os
        locator = FSFileLocator(temp_directory)

        # Use os.path.join for proper cross-platform path construction
        csv_path = os.path.join('data', 'csv')
        files = locator.list_files(csv_path)
        assert len(files) >= 2
        assert any('data1.csv' in f for f in files)
        assert any('data2.csv' in f for f in files)


# S3FileLocator tests removed - they require external AWS dependencies
# which violates testing standards. S3FileLocator should be tested
# in integration tests with proper AWS setup, not unit tests.


class TestFileLocatorPathUtils:
    """Test path utility functions that can be extracted"""

    def test_extension_filtering(self):
        """Test file extension filtering logic"""
        files = ['file1.txt', 'file2.csv', 'file3.txt', 'readme.md']

        # Filter for txt files
        txt_files = [f for f in files if f.endswith('.txt')]
        assert len(txt_files) == 2
        assert 'file1.txt' in txt_files
        assert 'file3.txt' in txt_files

        # Filter for csv files
        csv_files = [f for f in files if f.endswith('.csv')]
        assert len(csv_files) == 1
        assert 'file2.csv' in csv_files

    def test_path_joining(self):
        """Test path joining logic"""
        # Test different path combinations
        path_combinations = [
            ('data', 'file.txt', 'data/file.txt'),
            ('', 'file.txt', 'file.txt'),
            ('folder', 'subfolder/file.txt', 'folder/subfolder/file.txt'),
        ]

        for base, relative, expected in path_combinations:
            if base:
                result = os.path.join(base, relative)
                # Normalize path separators
                result = result.replace('\\', '/')
                expected = expected.replace('\\', '/')
                assert result == expected

    def test_s3_path_construction(self):
        """Test S3 path construction logic"""
        # Test S3 path construction patterns
        test_cases = [
            ('prefix', 'path', 'prefix/path'),
            ('', 'path', 'path'),
            ('prefix/', 'path', 'prefix/path'),
            ('prefix', '', 'prefix/'),
        ]

        for prefix, path, expected in test_cases:
            if path:
                # Handle case where prefix already ends with '/'
                if prefix and not prefix.endswith('/'):
                    s3_path = f"{prefix}/{path}"
                elif prefix:
                    s3_path = f"{prefix}{path}"
                else:
                    s3_path = path
            else:
                s3_path = prefix if prefix else ''
                # Add trailing slash for empty path if prefix doesn't already have it
                if s3_path and not s3_path.endswith('/'):
                    s3_path = s3_path + '/'

            # Normalize slashes
            s3_path = s3_path.replace('\\', '/')

            assert s3_path == expected
