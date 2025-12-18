# Entry Points and Job Factories

## Overview

This document explains the role of entry point scripts in the application and how they interact with Job Factories to enable modular, portable, and environment-agnostic job execution.

---

## What Are Entry Points?

Entry point scripts are the main scripts used to launch jobs in different environments (e.g., local containers, Databricks, AWS Glue). Examples include:

- `scripts/container/generic_entry.py`
- `scripts/databricks/generic_entry.py`
- `scripts/glue/generic_entry.py`

These scripts provide a unified interface for running jobs, handling environment-specific setup, argument parsing, and context injection.

---

## How Entry Points Work

1. **Argument Parsing:**  
   Entry points parse command-line arguments to determine which job module to run and with what parameters (e.g., `--module_name`).

2. **Dynamic Import:**  
   The specified job module is dynamically imported using the provided module name.

3. **Context Injection:**  
   Environment-specific context (such as `service_provider` or `has_spark`) is added to the job parameters.

4. **Delegation to Job Factory:**  
   The entry point calls the `main()` function of the imported job module, passing all relevant parameters.

---

## Interaction with Job Factories

- The job module's `main()` function is responsible for instantiating the appropriate Job Factory (e.g., `MyJobFactory`).
- The Job Factory receives configuration and dependencies, then constructs the job logic object.
- The Job Factory calls the job's `run()` method, which executes the business logic.

This separation ensures that:
- **Entry points** handle environment-specific concerns and parameter parsing.
- **Job Factories** handle job assembly, dependency injection, and execution.

---

## Example Flow

1. **Invocation:**  
   An entry point script is invoked (e.g., by Airflow, Databricks, Glue, or CLI) with `--module_name` and job parameters.

2. **Module Import:**  
   The entry point imports the specified job module and calls its `main()` function.

3. **Job Factory Usage:**  
   The job module's `main()` function creates a Job Factory, which assembles and runs the job.

---

## Benefits

- **Portability:** The same job logic can be executed in any supported environment.
- **Modularity:** Business logic is separated from environment-specific concerns.
- **Maintainability:** Standardized entry points and factories make the system easy to extend and maintain.

---

