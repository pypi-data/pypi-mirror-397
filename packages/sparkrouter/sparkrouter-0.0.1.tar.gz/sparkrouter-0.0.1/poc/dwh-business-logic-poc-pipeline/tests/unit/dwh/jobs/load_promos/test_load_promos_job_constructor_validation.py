"""
Unit tests for LoadPromosJob constructor validation
"""
import pytest
from dwh.jobs.load_promos.load_promos_job import LoadPromosJob
from dwh.jobs.load_promos.extract.promotion_extractor import PromotionExtractor
from dwh.jobs.load_promos.extract.extract_data_quality_validator import ExtractDataQualityValidator
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.transform.transform_data_quality_validator import TransformDataQualityValidator
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load.new_redshift_loader import DatabaseLoadStrategy
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load.unity_data_quality_validator import UnityDataQualityValidator
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from dwh.jobs.load_promos.load.stage_data_quality_validator import StageDataQualityValidator
from dwh.jobs.load_promos.load.redshift_data_quality_validator import RedshiftDataQualityValidator
from unit.noops import (
    ValidatingNoopNotificationService,
    ValidatingNoopDataSourceStrategy,
    ValidatingNoopDataSinkStrategy,
    NoopSchemaService
)


class TestLoadPromosJobConstructorValidation:
    """Unit tests for constructor validation in LoadPromosJob"""

    @pytest.fixture
    def valid_components(self):
        """Create valid job components"""
        from unit.noops import NoopThresholdEvaluator, NoopDatabaseLoadStrategy
        
        alarm_service = ValidatingNoopNotificationService()
        success_service = ValidatingNoopNotificationService()
        
        s3_source_strategy = ValidatingNoopDataSourceStrategy()
        promotion_extractor = PromotionExtractor(s3_source_strategy)
        
        threshold_evaluator = NoopThresholdEvaluator()
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        schema_service = NoopSchemaService()
        promotion_transformer = PromotionTransformer(schema_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)
        
        unity_sink_strategy = ValidatingNoopDataSinkStrategy()
        unity_loader = UnityLoader(unity_sink_strategy)
        unity_source_strategy = ValidatingNoopDataSourceStrategy()
        unity_dq_validator = UnityDataQualityValidator(unity_source_strategy, threshold_evaluator)
        
        stage_sink_strategy = ValidatingNoopDataSinkStrategy()
        stage_loader = StageLoader(stage_sink_strategy)
        stage_source_strategy = ValidatingNoopDataSourceStrategy()
        stage_dq_validator = StageDataQualityValidator(stage_source_strategy, threshold_evaluator)
        
        redshift_loader = NoopDatabaseLoadStrategy()
        redshift_source_strategy = ValidatingNoopDataSourceStrategy()
        redshift_dq_validator = RedshiftDataQualityValidator(redshift_source_strategy, threshold_evaluator)
        
        return {
            "alarm_service": alarm_service,
            "success_service": success_service,
            "promotion_extractor": promotion_extractor,
            "extract_dq_validator": extract_dq_validator,
            "promotion_transformer": promotion_transformer,
            "transform_dq_validator": transform_dq_validator,
            "unity_loader": unity_loader,
            "unity_dq_validator": unity_dq_validator,
            "stage_loader": stage_loader,
            "stage_dq_validator": stage_dq_validator,
            "redshift_loader": redshift_loader,
            "redshift_dq_validator": redshift_dq_validator
        }

    def test_valid_job_creation(self, valid_components):
        """Test that LoadPromosJob can be created with valid components"""
        job = LoadPromosJob(**valid_components)
        assert job is not None

    def test_invalid_alarm_service_type_fails(self, valid_components):
        """Test that invalid alarm_service type raises ValueError"""
        valid_components["alarm_service"] = "invalid_service"
        
        with pytest.raises(ValueError, match="alarm_service must be instance of NotificationService"):
            LoadPromosJob(**valid_components)

    def test_invalid_success_service_type_fails(self, valid_components):
        """Test that invalid success_service type raises ValueError"""
        valid_components["success_service"] = "invalid_service"
        
        with pytest.raises(ValueError, match="success_service must be instance of NotificationService"):
            LoadPromosJob(**valid_components)