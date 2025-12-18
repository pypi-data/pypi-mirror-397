class RawImageSchema:
    """RawImage Schema constants"""

    # Source schema (S3 Parquet extraction)
    SOURCE_SCHEMA_REF = "schemas/source/raw/raw_images.ddl"
    SOURCE_TABLE_NAME = "s3://bucket-name/path/to/jsonl/files"

    # Unity Catalog sink schema
    # UNITY_SCHEMA_REF = "schemas/sink/unity_catalog_v1_0.ddl"
    # UNITY_TABLE_NAME = "d_promotion_3_0"

    # Redshift core sink schema (also used for S3 staging)
    # REDSHIFT_CORE_SCHEMA_REF = "schemas/sink/redshift_dw_core_v1_0.ddl"
    # REDSHIFT_CORE_TABLE_NAME = "dw_core.d_promotion_3_0"


class TransformedImageSchema:
    """TransformedImage Schema constants"""
