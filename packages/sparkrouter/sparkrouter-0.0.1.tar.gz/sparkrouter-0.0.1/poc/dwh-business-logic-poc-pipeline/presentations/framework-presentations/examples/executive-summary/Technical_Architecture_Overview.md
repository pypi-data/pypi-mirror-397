# Technical Architecture Overview
## DWH Business Logic Framework

---

## Core Architecture Principles

### 1. Debug-First Development Philosophy
**"We write code once, but debug it endlessly"**

- **Platform independence**: Business logic runs anywhere, debugs everywhere
- **Local development**: Same business logic testable on dev machine
- **Explicit error handling**: Make failures traceable and actionable
- **Fail-fast approach**: No defensive programming or fallbacks

### 2. Schema-Centric Design
- **Everything revolves around schemas**: DDL files are source of truth
- **Automated validation**: All data operations validate against schemas
- **Change detection**: Schema evolution tracked automatically
- **Documentation generation**: Business glossary from schema annotations

### 3. Factory Pattern & Dependency Injection
- **Abstract factories**: Enable platform abstraction and testing
- **Precise parameters**: Concrete classes use exact parameter names
- **No kwargs in concrete implementations**: Only in abstract classes
- **Type annotations required**: All methods must be properly typed

---

## Framework Components

### Job Architecture
```
Entry Scripts (Platform-specific)
    ↓
Abstract Job Factory
    ↓
Concrete Job Implementation
    ↓
Service Layer (Data sources, sinks, schema, quality)
    ↓
Schema Services (DDL validation, type mapping)
```

### Service Categories
- **Data Sources**: Parquet, JDBC, Delta Lake with schema validation
- **Data Sinks**: Redshift, Postgres, S3, Unity Catalog
- **Schema Services**: DDL parsing, validation, change detection
- **Quality Services**: Threshold evaluation, anomaly detection
- **Infrastructure**: Email, notifications, database connections

### Testing Architecture
```
Unit Tests (Isolated Components)
├── Noop implementations for all dependencies
├── Fast feedback (seconds)
└── Component logic validation (95% coverage)

Functional Tests (Business Logic)
├── Real business logic components
├── Simulated I/O operations
└── End-to-end workflow validation (90% coverage)

Integration Tests (System Validation)
├── Docker containers
├── Real database interactions
└── Cross-platform validation (85% coverage)
```

---

## Multi-Platform Support

### Platform Abstraction
```python
# Same business logic everywhere
class LoadPromosJob(AbstractJob):
    def execute(self):
        extractor = self.factory.create_extractor()
        transformer = self.factory.create_transformer()
        loader = self.factory.create_loader()
        
        data = extractor.extract()
        processed = transformer.transform(data)
        loader.load(processed)

# Platform-specific entry points
# glue_entry.py, databricks_entry.py, local_entry.py
```

### Supported Platforms
- **AWS Glue**: Serverless Spark jobs
- **Databricks**: Unified analytics platform
- **Local Development**: Full production simulation
- **Docker Integration**: Isolated testing environment

### Configuration Management
- **spark-config.py**: Single source of truth for Spark settings
- **Environment parity**: Same configuration across all platforms
- **Version-aware**: Each version maintains independent config

---

## Version Management Architecture

### Complete Deployment Isolation
```
MWAA Orchestration (Unchanged)
├── DAG_A → Business Logic v1.0
├── DAG_B → Business Logic v1.1
└── DAG_C → Business Logic v2.0

S3 Deployment Structure:
business-logic/
├── v1.0/ (jobs/, schemas/, config/)
├── v1.1/ (jobs/, schemas/, config/)
└── v2.0/ (jobs/, schemas/, config/)
```

### Version Management Benefits
- **Zero MWAA changes**: DAG configuration change only
- **Instant rollback**: Switch version in <5 minutes
- **Parallel execution**: Multiple versions run simultaneously
- **Complete isolation**: No cross-version impact

### Technical Implementation
```python
class VersionedConfig:
    def __init__(self, version: str):
        self.version = version
        self.base_path = f"s3://bucket/business-logic/{version}/"
        
    def get_schema_path(self, schema_name: str) -> str:
        return f"{self.base_path}schemas/{schema_name}.ddl"
```

---

## Schema Management System

### DDL-Driven Architecture
```python
class DDLSchemaService:
    def validate_dataframe(self, df: DataFrame, table_name: str):
        expected_schema = self.ddl_reader.get_table_schema(table_name)
        
        if not self._schemas_match(expected_schema, df.schema):
            raise SchemaValidationError(
                f"Schema mismatch for {table_name}",
                expected=expected_schema,
                actual=df.schema,
                missing_fields=self._get_missing_fields(),
                extra_fields=self._get_extra_fields()
            )
```

### Automated Capabilities
- **Change detection**: Automatic DDL file monitoring
- **Impact analysis**: Dependency mapping for schema changes
- **Documentation generation**: Business glossary from DDL annotations
- **Validation enforcement**: Fail-fast on schema mismatches

---

## Data Quality Framework

### Threshold Evaluation
```python
class ThresholdEvaluationService:
    def evaluate_data_quality(self, df: DataFrame, thresholds: Dict):
        results = []
        for column, threshold in thresholds.items():
            null_percentage = df.filter(col(column).isNull()).count() / df.count()
            
            if null_percentage > threshold['max_null_percentage']:
                results.append(QualityViolation(
                    column=column,
                    violation_type="NULL_THRESHOLD_EXCEEDED",
                    actual_value=null_percentage,
                    threshold=threshold['max_null_percentage']
                ))
        return QualityResult(results)
```

### Quality Standards
- **PyArrow for test data**: Handles complex nested types
- **Microsecond timestamp precision**: Spark compatibility
- **Strict schema enforcement**: No inference or silent conversions
- **Comprehensive output validation**: Validate against sink schemas

---

## Testing Strategy Implementation

### Business Logic is Sacred Principle
- **Never mock business logic**: Only simulate external I/O
- **Real schema validation**: Use actual DDL files in all tests
- **Noop pattern**: Test doubles implement same interfaces
- **Validation preservation**: Test doubles maintain business constraints

### Three-Tier Testing Details
```python
# Unit Test Example
class TestPromotionProcessor:
    def test_process_promotions(self):
        processor = PromotionProcessor(
            data_source=NoopDataSource(),
            validator=NoopValidator()
        )
        result = processor.process_promotions()
        assert result.is_valid()

# Functional Test Example  
class TestLoadPromosJob:
    def test_end_to_end_processing(self):
        job = LoadPromosJobFactory().create_job(
            data_source_strategy=NoopParquetStrategy(),
            sink_strategy=NoopRedshiftStrategy()
        )
        job.execute()
        # Validate business logic with real transformations

# Integration Test Example
class TestLoadPromosIntegration:
    def test_docker_environment(self):
        # Real Postgres, Spark, MinIO containers
        job = LoadPromosJobFactory().create_job(**real_config)
        job.execute()
        # Validate actual database results
```

---

## Development Tooling

### Automated Environment Management
```bash
./setup-global-env.sh    # Global dependencies and tools
./setup-env.sh          # Project-specific virtual environment
./unit-tests.sh         # Fast isolated component testing
./functional-tests.sh   # Comprehensive business logic testing
./integration-tests.sh  # Full system validation with Docker
```

### Code Quality Enforcement
- **flake8 integration**: Stylistic compliance
- **Anti-pattern detection**: Automated validation (no Mocks)
- **Type annotation validation**: All methods properly typed
- **Testing standards**: Three-tier approach compliance

### Testing Optimization
```bash
# Developer workflow - targeted testing
./test-job.sh load_promos           # Single job testing
./test-component.sh promotion_transformer  # Component testing

# CICD workflow - comprehensive validation
./functional-tests.sh              # All jobs, all scenarios
./integration-tests.sh             # Cross-system validation
```

---

## Production Deployment

### Infrastructure as Code
```hcl
module "business_logic_framework" {
  source = "./modules/business-logic"
  
  version = "v1.0"
  environment = "production"
  
  code_bucket = aws_s3_bucket.business_logic_code
  schema_bucket = aws_s3_bucket.business_logic_schemas
  version_manifest_table = aws_dynamodb_table.version_manifest
}
```

### Monitoring & Observability
```python
class FrameworkMetrics:
    def record_job_execution(self, job_name: str, version: str, duration: float):
        cloudwatch.put_metric_data(
            Namespace='BusinessLogicFramework',
            MetricData=[{
                'MetricName': 'JobExecutionTime',
                'Dimensions': [
                    {'Name': 'JobName', 'Value': job_name},
                    {'Name': 'Version', 'Value': version}
                ],
                'Value': duration,
                'Unit': 'Seconds'
            }]
        )
```

---

## Security & Compliance

### Security Separation
- **Business logic layer**: Platform-agnostic, no permissions needed
- **Data access layer**: Service accounts with role-based access
- **Platform abstraction**: Same code, different execution contexts
- **Deployment layer**: Infrastructure as code manages permissions

### Compliance Features
- **Audit trails**: Complete history of business logic changes
- **Version tracking**: Immutable deployment history
- **Access controls**: Role-based service account management
- **Data lineage**: Automated documentation of data flows

---

## Performance Characteristics

### Benchmarking Results
- **No significant overhead**: Framework abstraction <1% performance impact
- **Memory efficiency**: Same memory usage as direct implementations
- **Execution time**: Comparable to platform-specific code
- **Scalability**: Linear scaling with data volume

### Optimization Strategies
- **Caching**: Frequently accessed schema and configuration data
- **Lazy loading**: Components instantiated only when needed
- **Resource pooling**: Database connections and Spark sessions
- **Platform-specific tuning**: Configuration-driven optimizations

---

## Future Architecture Considerations

### Extensibility Points
- **New platforms**: Easy addition through factory pattern
- **Additional data sources**: Plugin architecture for new connectors
- **Custom quality rules**: Extensible validation framework
- **Advanced testing**: Property-based testing integration

### Scalability Roadmap
- **Horizontal scaling**: Multi-job parallel execution
- **Performance optimization**: Advanced caching and resource management
- **Schema evolution**: Automated migration capabilities
- **Advanced monitoring**: ML-based anomaly detection