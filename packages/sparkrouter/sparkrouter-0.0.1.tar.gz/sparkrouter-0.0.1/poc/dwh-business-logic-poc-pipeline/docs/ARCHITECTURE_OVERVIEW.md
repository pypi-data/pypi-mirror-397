# Architecture Overview

## Key Principles

- **Modularity:** The application is structured around modular components (jobs, services, factories) that can be easily extended or replaced.
- **Portability:** Jobs can be executed in a variety of environments, including:
  - Local development (e.g., Docker, direct Python execution)
  - Databricks
  - AWS Glue
  - EMR
  - Any Spark-compatible or Python environment
- **Centralized Job Logic:** All business logic for jobs is centralized in Python classes, making it easy to reason about, test, and maintain. This reduces duplication and ensures consistent behavior across all execution platforms.

## High-Level Architecture

```
+-------------------+      +---------------------+      +-------------------+
|                   |      |                     |      |                   |
|  Job Factories    +----->+  Job Logic Classes  +----->+  Service Factories|
|                   |      |  (e.g. RevenueRecon)|      |  (DB, Email, etc) |
+-------------------+      +---------------------+      +-------------------+
        |                          |                             |
        |                          |                             |
        v                          v                             v
+-----------------------------------------------------------------------+
|                        Execution Environments                         |
|  (Local, Databricks, Glue, EMR, etc.)                                 |
+-----------------------------------------------------------------------+
```

- **Job Factories:** Responsible for assembling jobs with the correct configuration and dependencies for the target environment.
- **Job Logic Classes:** Contain the core business logic, agnostic to the execution environment.
- **Service Factories:** Provide environment-specific implementations for services (database, email, notifications, Spark, etc.).

## Execution Flow

1. **Configuration:** Jobs are configured via parameterized factories, allowing for environment-specific overrides.
2. **Dependency Injection:** Factories inject the appropriate service implementations (e.g., JDBC, Spark, email) based on configuration and runtime context.
3. **Execution:** The same job logic runs identically across all environments, ensuring consistency and simplifying debugging.
4. **Extensibility:** New jobs or services can be added with minimal changes to the existing codebase.

## Benefits

- **Consistency:** Centralized logic ensures jobs behave the same way everywhere.
- **Testability:** Modular design enables isolated unit and integration testing.
- **Portability:** Minimal code changes are required to run jobs in new environments.
- **Maintainability:** Clear separation of concerns and centralized configuration make the system easy to extend and maintain.

## Example: Revenue Recon Job

- The `RevenueReconJobFactory` assembles the job using configuration and injects services (database, email, notification).
- The `RevenueReconJob` contains all business logic, independent of where it runs.
- The same job can be executed locally, in Databricks, Glue, or EMR by simply changing configuration or entrypoint.

## Extending the Architecture

- To add a new job, implement a new job logic class and a corresponding factory.
- To support a new environment or service, implement a new service factory or provider.


