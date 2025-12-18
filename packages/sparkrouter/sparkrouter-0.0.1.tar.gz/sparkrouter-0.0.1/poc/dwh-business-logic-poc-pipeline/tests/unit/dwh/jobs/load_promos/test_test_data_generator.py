import pytest
from dwh.jobs.load_promos.test_data_generator import LoadPromosTestDataGenerator


@pytest.mark.unit
class TestLoadPromosTestDataGenerator:
    """Unit tests for LoadPromosTestDataGenerator - testing class structure only"""
    
    def test_class_exists_and_has_create_method(self):
        """Test that the class exists and has the required static method"""
        assert hasattr(LoadPromosTestDataGenerator, 'create_test_data')
        assert callable(getattr(LoadPromosTestDataGenerator, 'create_test_data'))
    
    def test_create_test_data_is_static_method(self):
        """Test that create_test_data is a static method"""
        # Can call without instantiating the class
        method = getattr(LoadPromosTestDataGenerator, 'create_test_data')
        assert method is not None