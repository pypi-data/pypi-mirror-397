# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a proof-of-concept Data Warehouse (DWH) Business Logic framework that provides a platform-agnostic approach for running data processing jobs across multiple execution environments (Databricks, AWS Glue, EMR, Docker containers). The framework emphasizes modular design, comprehensive testing, and strict schema validation.

## Core Architecture

### Factory Pattern + Dependency Injection
- **Job Factories** assemble jobs with environment-specific configuration and dependencies
- **Service Factories** provide environment-specific implementations (database, email, Spark, etc.)
- **Job Logic Classes** contain business logic that's agnostic to execution environment
- Dependencies are ALWAYS injected, never created inside classes

### Three-Layer Job Architecture
```
Entry Points (generic_entry.py)
  ↓ (environment-specific setup)
Job Factories (AbstractJobFactory subclasses)
  ↓ (dependency injection & configuration)
Job Classes (AbstractJob subclasses)
  ↓ (business logic execution)
```

### Key Design Patterns
- **Factory Pattern**: For creating complex objects with proper dependencies
- **Template Method**: AbstractJob.run() is final; subclasses implement execute_job(), on_success(), on_failure()
- **Strategy Pattern**: Configuration-driven strategy selection (data sources, sinks, notifications)

### RULE: No Re-exports in `__init__.py`
- `__init__.py` files should be empty or contain only `__all__` declarations
- NEVER import and re-export modules in `__init__.py` (e.g., `from .module import Class`)
- This practice obfuscates where code actually lives and makes following imports harder
- Always use direct imports from the actual module: `from dwh.services.quality.quality_models import QualityResult`
- NOT: `from dwh.services.quality import QualityResult`

### Schema-Centric Philosophy
- EVERYTHING revolves around schemas - they are the foundation of all business logic
- All data operations MUST validate against real production DDL files
- Schema validation failures must be explicit and actionable
- Tests MUST use actual production DDL files, never test-specific overrides

## Common Development Commands

### Environment Setup
```bash
# Setup development environment (creates venv, installs dependencies)
./setup-env.sh
```

### Testing

**IMPORTANT**: The user runs pytest manually in WSL. Do NOT run pytest commands directly - the user will run tests themselves and report results.

```bash
# Run unit tests only
./unit-tests.sh [test_directory]

# Run functional tests (tests business logic with local execution)
pytest -m functional

# Run integration tests (uses Docker containers)
./integration-tests.sh

# Run all tests with coverage report
./run-coverage.sh
```

### Running Single Tests
```bash
# Run specific test file
pytest tests/unit/path/to/test_file.py -v

# Run specific test method
pytest tests/unit/path/to/test_file.py::TestClass::test_method -v

# Run with specific markers
pytest -m "unit and not integration" -v
```

### Code Quality
```bash
# Validate code with flake8
./code-validation.sh [source_directory] [flake8_config]
```

### Building & Deployment
```bash
# Full build (validation + tests + package)
./build.sh

# Build without validation
./build.sh --no-validate

# Build without tests
./build.sh --no-tests

# Build with custom version
./build.sh --version=X.Y.Z

# Full deployment (build + integration tests + S3 upload)
./deploy.sh

# Deploy without integration tests
./deploy.sh --no-integration
```

### Docker-Based Execution
```bash
# Run Spark job in container
./docker/spark/spark-submit.sh \
  --module_name dwh.jobs.spark_example.spark_example_job_factory

# Run Python job in container
./docker/python/python-submit.sh \
  --module_name dwh.jobs.generic_example.generic_example_job_factory
```

## Critical Development Standards

### RULE: Business Logic is Sacred
- Business logic is the highest priority and MUST NEVER be compromised for testing convenience
- Tests must be adapted to work with business logic, not the other way around
- If business logic is hard to test, refactor the architecture to make it more testable
- Implementation must match documented business specifications exactly

### RULE: No Mocks or Patches
- NEVER use Mock, Patch, or monkeypatching in any test type
- Use Noop implementations that implement the same interface as real components
- Noop implementations MUST preserve all validation and business constraint logic
- Only simulate external I/O operations (database, file system, network)

### RULE: Fail-Fast Philosophy
- If something is not working, throw an exception immediately
- Do NOT create fallbacks, default behaviors, or fallback values
- Make failures explicit so underlying issues can be fixed
- If a dependency is required, make it required and fail fast if not provided

### RULE: Precise Parameters Required
- **kwargs are ONLY allowed in abstract classes and factories
- Concrete implementations MUST use precise, named parameters
- Method parameters and return types must be type-annotated
- Variables are expected and can NEVER be set to default values
- Do not check for null or provide default values

### RULE: No Stubbed Implementations
- Stubbed or incomplete methods must raise NotImplementedError
- Do not leave TODO comments or empty method bodies
- Include descriptive error messages explaining what needs to be implemented

### RULE: Use Mermaid for Diagrams
- When creating diagrams in markdown files, use Mermaid syntax instead of ASCII art
- Mermaid renders properly in GitHub, GitLab, and most markdown viewers
- Common diagram types: flowchart, sequenceDiagram, classDiagram, stateDiagram

## Three-Tier Testing Strategy

### Unit Tests (`tests/unit/`)
**Purpose**: Test individual components in complete isolation
- Use Noop implementations for ALL dependencies
- Focus on component logic, validation, and error handling
- Should be fast and require no external resources
- Run with: `./unit-tests.sh`

### Functional Tests (`tests/functional/`)
**Purpose**: Test complete business workflows with real processing logic
- **NEVER mock, stub, or replace business logic**
- Use real DDL schema services with actual DDL files
- Test complete end-to-end business workflows
- Exercise all business logic components in sequence
- Use Noop strategies only for backend I/O (must still validate schemas)
- Run with: `pytest -m functional`

### Integration Tests (`tests/integration/`)
**Purpose**: Test interactions between multiple real components via Docker containers
- Use real implementations where possible, Noop only for external systems
- Test actual system integration points
- **NO local Spark sessions** - complete Docker isolation required
- Use pandas/pyarrow for test data generation, NOT Spark
- Run with: `./integration-tests.sh`

### CRITICAL: Why No Local Spark in Integration Tests
- Local Spark sessions auto-discover Docker Spark masters at exposed ports
- This creates Python version conflicts between local environment and containers
- Maintains clean separation: local = orchestration, Docker = Spark processing

## Data Processing Standards

### PyArrow for Integration Test Data
- Integration test data MUST be generated using PyArrow (not pandas)
- Test data MUST match functional test data exactly
- Dynamic generation ensures consistency with functional tests

### Timestamp Precision
- ALL timestamps MUST use microsecond precision (Spark's default)
- NO nanosecond precision (pandas default causes incompatibility)

### Complex Type Support
- ALL complex nested types MUST be native parquet structures
- NO JSON string representations of complex types

### Strict Schema Validation
- ALL data reads MUST enforce exact schema match
- NO schema inference or best-effort parsing
- ANY schema mismatch MUST cause immediate failure
- Schema changes must break tests until business logic is updated

## Project Structure

```
src/dwh/
├── data/              # Data model classes (DL Base layer)
├── jobs/              # Job implementations
│   ├── load_promos/   # Example ETL job
│   ├── transform_images/
│   └── revenue_recon/
├── services/          # Service abstractions
│   ├── data_source/   # Data source strategies (Parquet, Delta, JDBC)
│   ├── data_sink/     # Data sink strategies (Delta, Postgres, Redshift)
│   ├── database/      # Database connections
│   ├── schema/        # Schema services (DDL readers, validators)
│   ├── spark/         # Spark session management
│   ├── email/         # Email notifications
│   └── notification/  # Notification services
└── utils/             # Utility functions

scripts/
├── container/         # Container entry points
├── databricks/        # Databricks entry points
└── glue/              # AWS Glue entry points

tests/
├── unit/              # Isolated component tests
├── functional/        # Business logic workflow tests
└── integration/       # Docker-based system tests
```

## Job Development Workflow

### Creating a New Job

1. **Create Job Class** extending AbstractJob in `src/dwh/jobs/your_job/`
   - Implement `execute_job(**kwargs)` with business logic
   - Implement `on_success(results)` for success handling
   - Implement `on_failure(error_message)` for error handling

2. **Create Job Factory** extending AbstractJobFactory
   - Implement `create_job(**kwargs)` to assemble job with dependencies
   - Parse configuration from kwargs
   - Inject required services (database, email, notification, etc.)

3. **Add main() function** to factory module
   ```python
   def main(**kwargs):
       factory = YourJobFactory()
       return factory.run(**kwargs)
   ```

4. **Write Comprehensive Tests**
   - Unit tests for isolated components
   - Functional tests for complete business logic workflow
   - Integration tests for system interactions (if needed)

5. **Document Configuration Schema** in job's README or docstrings

## Configuration Patterns

Jobs are configured via JSON passed through command-line arguments:

```bash
--module_name dwh.jobs.load_promos.load_promos_job_factory \
--load_promos_job '{
  "extractor_config": {"strategy": "PARQUET", "source_table": "s3a://..."},
  "unity_loader_config": {"strategy": "DELTA", "path": "s3a://..."},
  "redshift_loader_config": {
    "strategy": "POSTGRES",
    "jdbc_url": "jdbc:postgresql://...",
    "properties": {"user": "...", "password": "..."}
  },
  "job_failed_notifications": {"notification_service": "EMAIL"},
  "job_success_notifications": {"notification_service": "NOOP"}
}'
```

## Execution Environments

The same job logic runs across all platforms:

- **Local Docker**: Development and testing
- **Databricks**: Collaborative development with Unity Catalog
- **AWS Glue**: Serverless, event-driven ETL
- **EMR**: Cost-sensitive, long-running batch processing

Platform-specific behavior is handled through:
- `service_provider` parameter (DATABRICKS, GLUE, EMR, CONTAINER)
- `has_spark` flag for Spark-dependent jobs
- Environment-specific service factories

## Important Files & Documentation

- `DEVELOPMENT_PHILOSOPHY.md` - Core development principles and philosophy
- `docs/ARCHITECTURE_OVERVIEW.md` - High-level architecture explanation
- `docs/ENTRY_POINTS_AND_JOB_FACTORIES.md` - Job execution flow
- `docs/JOB_EXECUTION_ARCHITECTURE.md` - Detailed job execution patterns
- `COVERAGE_STRATEGIES.md` - Coverage measurement approaches
- `.github/copilot/CRITICAL_Testing_Standards.md` - Testing requirements
- `.github/copilot/CRITICAL_Design_Standards.md` - Design patterns
- `.github/copilot/DATA_STANDARDS.md` - Data processing requirements

## Common Patterns

### Service Factory Usage
```python
# Create data source
source = DataSourceStrategyFactory.create_data_source_strategy(
    strategy_type="PARQUET",
    source_table="s3a://bucket/path"
)

# Create data sink
sink = DataSinkStrategyFactory.create_data_sink_strategy(
    strategy_type="DELTA",
    sink_path="s3a://bucket/output"
)
```

### Noop Implementation Pattern
```python
class NoopEmailService(EmailService):
    """Test double that simulates email service without sending emails"""

    def send_email(self, to: str, subject: str, body: str) -> None:
        # Validate inputs (preserve business logic validation)
        if not to or "@" not in to:
            raise ValueError(f"Invalid email address: {to}")
        if not subject:
            raise ValueError("Email subject is required")

        # Simulate I/O without actually sending
        self.logger.info(f"NOOP: Would send email to {to}")
```

## Debug-First Development

When encountering problems:
1. Write a focused test that isolates and reproduces the issue
2. Use the test to verify the fix works correctly
3. Add the test to the suite to prevent regression
4. This approach improves test coverage while solving real problems

## Coverage Targets

- **Primary Goal**: 80% combined coverage (unit + functional + integration)
- **Schema Drift Detection**: 95% confidence in catching schema evolution issues
- **Business Logic Validation**: 95% confidence in business logic correctness

Check current coverage: `./run-coverage.sh` (generates HTML reports in `htmlcov_combined/`)

## Version Management

Version is stored in `VERSION` file (currently 0.3.0)
- Used by `setup.py` for package versioning
- Can be overridden with `--version` flag in build/deploy scripts

## Windows Considerations

This project includes bash scripts (`.sh` files) that are designed for Unix-like environments. On Windows, you may need:
- WSL (Windows Subsystem for Linux)
- Git Bash
- Or adapt commands to PowerShell equivalents
