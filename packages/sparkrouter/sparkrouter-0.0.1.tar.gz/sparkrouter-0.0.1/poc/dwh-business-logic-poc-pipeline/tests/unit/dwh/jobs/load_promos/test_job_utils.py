import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from dwh.jobs.load_promos.job_utils import JobUtils


class TestJobUtils:

    def test_parse_date_to_datetime_iso_format(self):
        """Test parsing ISO format date string"""
        result = JobUtils.parse_date_to_datetime("2023-12-25T10:30:00Z", "test_param")
        expected = datetime(2023, 12, 25, 10, 30, 0, tzinfo=ZoneInfo('UTC'))
        assert result == expected

    def test_parse_date_to_datetime_standard_format(self):
        """Test parsing standard format date string"""
        result = JobUtils.parse_date_to_datetime("2023-12-25 10:30:00", "test_param")
        expected = datetime(2023, 12, 25, 10, 30, 0, tzinfo=ZoneInfo('UTC'))
        assert result == expected

    def test_parse_date_to_datetime_date_only_format(self):
        """Test parsing date-only format string"""
        result = JobUtils.parse_date_to_datetime("2023-12-25", "test_param")
        expected = datetime(2023, 12, 25, 0, 0, 0, tzinfo=ZoneInfo('UTC'))
        assert result == expected

    def test_parse_date_to_datetime_invalid_format_raises_error(self):
        """Test that invalid date format raises ValueError"""
        with pytest.raises(ValueError, match="Could not parse test_param"):
            JobUtils.parse_date_to_datetime("invalid-date", "test_param")

    def test_parse_date_to_datetime_ensures_utc_timezone(self):
        """Test that result always has UTC timezone"""
        result = JobUtils.parse_date_to_datetime("2023-12-25", "test_param")
        assert result.tzinfo == ZoneInfo('UTC')

    def test_read_file(self, tmp_path):
        """Test reading file content"""
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content, encoding='utf-8')
        
        result = JobUtils.read_file(str(test_file))
        assert result == test_content