"""
Centralized schema constants for the load_promos job.

This module consolidates all schema references and table names used
throughout the load_promos job components, providing a single source
of truth for schema-related configuration.
"""


class LoadPromosSchema:
    """Schema constants for the load_promos job"""
    
    # Source schema (S3 Parquet extraction)
    SOURCE_SCHEMA_REF = "schemas/source/dl_base_v1_0.ddl"
    SOURCE_TABLE_NAME = "ecom_sflycompromotion_promotions"
    
    # Unity Catalog sink schema
    UNITY_SCHEMA_REF = "schemas/sink/unity_catalog_v1_0.ddl"
    UNITY_TABLE_NAME = "d_promotion_3_0"
    
    # Redshift core sink schema (also used for S3 staging)
    REDSHIFT_CORE_SCHEMA_REF = "schemas/sink/redshift_dw_core_v1_0.ddl"
    REDSHIFT_CORE_TABLE_NAME = "dw_core.d_promotion_3_0"
