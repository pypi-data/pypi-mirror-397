# Load Promos Job Architecture

## Overview

The Load Promos Job is a modern ETL pipeline that extracts promotion data from S3 parquet files, transforms it according to business rules, and loads it primarily to Unity Catalog with secondary loading to Redshift/PostgreSQL via S3 staging. Comprehensive data quality validation occurs at each stage.

## Architecture Principles

- **Single Responsibility**: Each component has one clear purpose
- **Strategy Pattern**: Database loading adapts to different targets (Redshift/PostgreSQL)
- **In-Memory Processing**: No intermediate storage until final destinations
- **Hierarchical Loading**: Unity Catalog is primary, Redshift is secondary via staging
- **Fail Fast**: Validation happens before expensive operations
- **Schema-First**: All operations validate against production DDL schemas

## Component Structure

```
load_promos/
├── extract/
│   ├── promotion_extractor.py          # S3 parquet data extraction
│   └── extract_data_quality_validator.py # Raw data validation
├── transform/
│   ├── promotion_transformer.py        # Business logic transformation
│   └── transform_data_quality_validator.py # Transformed data validation
├── load/
│   ├── unity_loader.py                 # Unity Catalog Delta loading
│   ├── unity_data_quality_validator.py # Unity data validation
│   ├── stage_loader.py                 # S3 staging parquet loading
│   ├── stage_data_quality_validator.py # Staging data validation
│   ├── new_redshift_loader.py          # Database loading strategies
│   └── redshift_data_quality_validator.py # Database data validation
├── load_promos_job.py                  # Main orchestration
├── load_promos_job_factory.py          # Dependency injection factory
├── load_promos_schema.py               # Schema constants
└── job_utils.py                        # Utility functions
```

## Execution Flow

```
S3 Parquet Source
    ↓
[Extract Phase]
    PromotionExtractor → ExtractDataQualityValidator
    ↓
[Transform Phase]
    PromotionTransformer → TransformDataQualityValidator
    ↓
[Load Phase - Sequential]
    1. UnityLoader → UnityDataQualityValidator (PRIMARY)
    2. StageLoader → StageDataQualityValidator (for Redshift COPY)
    3. DatabaseLoadStrategy → RedshiftDataQualityValidator (SECONDARY)
```

## Core Components

### 1. Extract Phase

**PromotionExtractor**
- Reads promotion data from S3 parquet files using DataSourceStrategy
- Applies date filtering based on `ptn_ingress_date` and `updatedate`
- Enforces source schema validation via LoadPromosSchema.SOURCE_SCHEMA_REF

**ExtractDataQualityValidator**
- Validates raw data integrity (schema compliance, null checks, required fields)
- Uses ThresholdEvaluator for configurable validation rules
- Fails fast on data quality issues

### 2. Transform Phase

**PromotionTransformer**
- Flattens complex nested structures from source schema
- Applies business transformation rules:
  - Maps nested fields to flat PostgreSQL schema
  - Extracts SKU lists from arrays of structs
  - Concatenates bundle SKUs across multiple bundles
  - Formats properties flags as key-value strings
  - Applies deduplication logic (latest updatedate wins)
- Enforces exact target schema using schema service

**TransformDataQualityValidator**
- Validates transformed data against business rules
- Checks for duplicates, referential integrity
- Validates business logic transformations

### 3. Load Phase

**UnityLoader (PRIMARY DESTINATION)**
- Main target for promotion data using Delta format
- Supports merge/upsert operations for incremental loads
- Uses DataSinkStrategy for Unity Catalog configuration
- Business-critical data lake storage

**StageLoader (REDSHIFT COPY SUPPORT ONLY)**
- Exists solely to support Redshift COPY operations
- Writes transformed data to S3 staging area as parquet
- Intermediate step - not a final destination
- Partitions data for efficient Redshift loading

**DatabaseLoadStrategy (SECONDARY DESTINATION)**
- **PostgresLoadStrategy**: Reads from S3 staging, transforms in Spark, writes via JDBC
- **RedshiftLoadStrategy**: Uses native COPY command from S3 staging to Redshift, then MERGE to core tables
- Provides traditional data warehouse access patterns

**Data Quality Validators**
- Each loader has corresponding validator that verifies successful data loading
- Validates row counts, schema compliance, and data integrity
- Uses actual data source strategies to read back and verify loaded data

## Schema Management

**LoadPromosSchema**
- Centralizes all schema references and table names
- Source: `schemas/source/dl_base_v1_0.ddl` → `ecom_sflycompromotion_promotions`
- Unity: `schemas/sink/unity_catalog_v1_0.ddl` → `d_promotion_3_0`
- Redshift: `schemas/sink/redshift_dw_core_v1_0.ddl` → `dw_core.d_promotion_3_0`

## Factory Pattern

**LoadPromosJobFactory**
- Implements dependency injection for all components
- Creates appropriate strategies based on configuration
- Handles Spark session management
- Configures notification services for success/failure/data quality alerts

## Configuration

```json
{
  "extractor_config": {
    "strategy": "PARQUET",
    "source_table": "s3a://bucket/path/to/parquet/"
  },
  "unity_loader_config": {
    "strategy": "DELTA",
    "path": "s3a://bucket/unity-catalog/promotions/d_promotion_3_0/"
  },
  "stage_loader_config": {
    "strategy": "PARQUET", 
    "path": "s3a://bucket/staging/promotions/"
  },
  "redshift_loader_config": {
    "strategy": "REDSHIFT",
    "jdbc_url": "jdbc:postgresql://redshift-cluster:5439/warehouse",
    "s3_staging_path": "s3a://bucket/staging/promotions/",
    "properties": {
      "user": "redshift_user",
      "password": "redshift_password",
      "driver": "org.postgresql.Driver"
    },
    "aws_credentials": {
      "access_key": "AKIA...",
      "secret_key": "..."
    }
  },
  
  // Alternative configuration for integration testing
  "redshift_loader_config": {
    "strategy": "POSTGRES",
    "jdbc_url": "jdbc:postgresql://postgres:5432/postgres_db",
    "properties": {
      "user": "postgres_user",
      "password": "postgres_password",
      "driver": "org.postgresql.Driver"
    }
  },
  "job_success_notifications": {
    "notification_service": "EMAIL",
    "recipients": ["team@company.com"]
  },
  "job_failed_notifications": {
    "notification_service": "SLACK",
    "channels": ["#critical-alerts"]
  },
  "data_quality_notifications": {
    "notification_service": "SNS",
    "topic_arn": "arn:aws:sns:region:account:dq-alerts"
  }
}
```

## Key Design Decisions

### 1. Strategy Pattern for Database Loading
- Allows switching between Redshift (native COPY) and PostgreSQL (JDBC) without code changes
- Encapsulates database-specific loading logic
- Enables testing with PostgreSQL while deploying to Redshift

### 2. Hierarchical Loading Strategy
- Unity Catalog is the primary destination for business data
- Redshift is secondary, providing traditional data warehouse access
- S3 staging exists only to support efficient Redshift COPY operations
- Sequential loading ensures data consistency across destinations

### 3. Schema-First Validation
- All operations validate against production DDL files
- Schema changes break tests until business logic is updated
- Prevents schema drift and deployment issues

### 4. In-Memory Processing
- No intermediate storage between extract/transform phases
- Reduces I/O overhead and storage costs
- Simplifies error handling and recovery

## Event Notifications

The Load Promos Job implements comprehensive event notification system to alert stakeholders of job status and data quality issues.

### Notification Types

**Job Success Notifications**
- Sent when entire job completes successfully
- Includes execution summary and completion timestamp
- Configured via `job_success_notifications` in job configuration
- Subject: "LoadPromosJob: Job Execution Successful"

**Job Failure Notifications**
- Sent when job fails at any stage (extract, transform, or load)
- Includes error details and failure location
- Configured via `job_failed_notifications` in job configuration
- Subject: "LoadPromosJob: Job Execution Failed"

**Data Quality Notifications**
- Sent when data quality validation fails at any stage
- Includes specific validation failures and threshold violations
- Configured via `data_quality_notifications` in job configuration
- Triggered by ThresholdEvaluator across all DQ validators
- Examples:
  - Extract DQ: Schema violations, missing required fields
  - Transform DQ: Business rule violations, duplicate records
  - Load DQ: Row count mismatches, referential integrity failures

### Notification Configuration

```json
{
  "job_success_notifications": {
    "notification_service": "EMAIL|SLACK|SNS|NOOP",
    "recipients": ["team@company.com"],
    "channels": ["#data-alerts"]
  },
  "job_failed_notifications": {
    "notification_service": "EMAIL|SLACK|SNS|NOOP",
    "recipients": ["oncall@company.com"],
    "channels": ["#critical-alerts"]
  },
  "data_quality_notifications": {
    "notification_service": "EMAIL|SLACK|SNS|NOOP",
    "recipients": ["data-quality@company.com"],
    "channels": ["#dq-alerts"]
  }
}
```

### Notification Strategy Pattern

- Uses NotificationServiceFactory to create appropriate notification services
- Supports multiple notification channels (Email, Slack, SNS, etc.)
- NOOP implementation for testing and development environments
- Configurable per environment and notification type

## Data Quality Framework

- **Extract DQ**: Raw data validation (nulls, schema, basic constraints)
- **Transform DQ**: Business rule validation (duplicates, relationships)
- **Load DQ**: Post-load validation (row counts, referential integrity)
- **Threshold-Based**: Configurable thresholds for data quality metrics
- **Notification Integration**: Alerts sent via data quality notification service

## Testing Strategy

- **Unit Tests**: Individual component testing with Noop implementations
- **Functional Tests**: End-to-end business logic testing with real Spark
- **Integration Tests**: Full pipeline testing with Docker containers
- **Schema Validation**: All tests use production DDL files

## Deployment

- **Containerized**: Runs in Docker with Spark cluster
- **Configuration-Driven**: Environment-specific configs via JSON
- **Monitoring**: Comprehensive logging and notification integration
- **Scalable**: Spark-based processing scales with data volume