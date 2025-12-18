"""
Abstract base class for schema-specific data builders
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dwh.services.schema.schema_service import SchemaService


class SchemaDataBuilder(ABC):
    """
    Abstract base class for schema-specific data builders
    
    Provides a foundation for creating test data that conforms to DDL schemas.
    Supports both fluent builder patterns and bulk record generation with
    automatic schema validation against real DDL files.
    
    CORE CONCEPTS:
    - Schema-driven: All records validated against real DDL schemas
    - Fluent interface: Chainable methods for building complex records
    - Bulk generation: Create multiple similar records with variations
    - Validation: Early detection of schema compliance issues
    
    USAGE PATTERNS:
    
    # Pattern 1: Single record with fluent interface
    builder = PromotionDataBuilder(schema_service)
    record = (builder
              .with_id("PROMO_001")
              .with_name("Black Friday Sale")
              .with_promotion_type("PERCENTAGE_DISCOUNT")
              .to_records()[0])
    
    # Pattern 2: Multiple records with add_records()
    builder = PromotionDataBuilder(schema_service)
    records = (builder
               .add_records(5, 
                           name="Holiday Sale", 
                           properties_promotionType="FIXED_DISCOUNT")
               .to_records())
    # Creates 5 records with IDs: PROMO_001_000, PROMO_001_001, etc.
    
    # Pattern 3: Mixed approach - base records + fluent modifications
    builder = PromotionDataBuilder(schema_service)
    builder.add_records(3, name="Base Sale")
    
    # Modify specific records
    premium_records = (builder
                       .with_promotion_type("PERCENTAGE_DISCOUNT")
                       .with_tags("PREMIUM", "VIP")
                       .to_records())
    
    # Pattern 4: Template-based generation
    base_builder = PromotionDataBuilder(schema_service).add_record(name="Template")
    
    variations = [
        base_builder.with_promotion_type("PERCENTAGE_DISCOUNT").to_records(),
        base_builder.with_promotion_type("FIXED_DISCOUNT").to_records(),
        base_builder.with_promotion_type("BOGO").to_records()
    ]
    
    SCHEMA VALIDATION:
    - Validates field presence against DDL schema
    - Catches missing required fields
    - Detects extra fields not in schema
    - Fails fast on schema violations
    
    SERIALIZATION:
    Use DataSerializer for converting records to various formats:
    
    records = builder.to_records()
    df = DataSerializer.to_dataframe(records, spark, schema)
    DataSerializer.to_parquet(records, "output.parquet", spark, schema)
    """
    
    def __init__(self, schema_service: SchemaService):
        self.schema_service = schema_service
        self.records: List[Dict[str, Any]] = []
        self._schema = None
    
    @property
    @abstractmethod
    def schema_ref(self) -> str:
        """Return the schema reference for this builder"""
        pass
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the table name for this builder"""
        pass
    
    @property
    def schema(self):
        """Get schema from schema service (cached)"""
        if self._schema is None:
            self._schema = self.schema_service.get_schema(self.schema_ref, self.table_name)
        return self._schema
    
    @abstractmethod
    def create_default_record(self) -> Dict[str, Any]:
        """Create a default record with all required fields populated"""
        pass
    
    def add_record(self, **overrides) -> 'SchemaDataBuilder':
        """Add a record with optional field overrides"""
        record = self.create_default_record()
        record.update(overrides)
        self.records.append(record)
        return self
    
    def add_records(self, count: int, **base_overrides) -> 'SchemaDataBuilder':
        """
        Add multiple records with base overrides and unique IDs
        
        Creates 'count' number of records, each starting with the default record
        and applying the base_overrides. Automatically generates unique IDs by
        appending a 3-digit suffix to ID fields.
        
        Args:
            count: Number of records to create
            **base_overrides: Field values to apply to all records
        
        Returns:
            Self for method chaining
        
        Example:
            # Creates 3 promotion records with unique IDs
            builder.add_records(3, 
                               name="Holiday Sale",
                               properties_promotionType="FIXED_DISCOUNT")
            
            # Results in records with IDs:
            # - PROMO_DEFAULT_001_000
            # - PROMO_DEFAULT_001_001  
            # - PROMO_DEFAULT_001_002
        """
        for i in range(count):
            overrides = base_overrides.copy()
            # Add unique suffix to ID fields if they exist
            for field_name in ['_id', 'id', 'promotionid']:
                if field_name in overrides:
                    overrides[field_name] = f"{overrides[field_name]}_{i:03d}"
            self.add_record(**overrides)
        return self
    
    def clear(self) -> 'SchemaDataBuilder':
        """Clear all records"""
        self.records.clear()
        return self
    
    def to_records(self) -> List[Dict[str, Any]]:
        """
        Get all generated records with schema validation
        
        Validates all records against the DDL schema before returning.
        This ensures schema compliance and catches issues early.
        
        Returns:
            List of validated record dictionaries
        
        Raises:
            ValueError: If any record fails schema validation
        
        Example:
            records = builder.to_records()
            # All records are guaranteed to be schema-compliant
        """
        # Validate all records against schema before returning
        for i, record in enumerate(self.records):
            self._validate_record(record, i)
        return self.records.copy()
    
    def _validate_record(self, record: Dict[str, Any], record_index: int) -> None:
        """Validate a single record against the schema"""
        schema = self.schema
        schema_fields = {field.name for field in schema.fields}
        record_fields = set(record.keys())
        
        # Check for missing required fields
        missing_fields = schema_fields - record_fields
        if missing_fields:
            raise ValueError(f"Record {record_index} missing required fields: {missing_fields}")
        
        # Check for extra fields not in schema
        extra_fields = record_fields - schema_fields
        if extra_fields:
            raise ValueError(f"Record {record_index} has extra fields not in schema: {extra_fields}")
    
    def _ensure_record_copy(self) -> 'SchemaDataBuilder':
        """
        Ensure we have at least one record and return a copy for fluent interface
        
        This method enables the fluent builder pattern by:
        1. Creating a default record if none exist
        2. Creating a new builder instance with copied records
        3. Allowing method chaining without mutating the original builder
        
        Returns:
            New builder instance with copied records
        
        Note:
            This is used internally by fluent methods like with_id(), with_name(), etc.
        """
        if not self.records:
            self.add_record()
        
        # Create new builder instance with copied records
        new_builder = self.__class__(self.schema_service)
        new_builder.records = [record.copy() for record in self.records]
        return new_builder
    
    def count(self) -> int:
        """Get number of records"""
        return len(self.records)
