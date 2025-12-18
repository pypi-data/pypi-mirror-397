# Versioning and Safe Job Migration

## Overview

This framework is designed to support robust versioning and safe migration of data pipeline jobs. By following best practices for version management, you can introduce new features, refactor jobs, or make breaking changes without disrupting existing workflows or dependencies.

---

## Versioning Strategy

- **Semantic Versioning:**  
  The project uses semantic versioning (MAJOR.MINOR.PATCH) to clearly communicate the impact of changes.
    - **MAJOR:** Breaking changes or incompatible API updates.
    - **MINOR:** Backwards-compatible feature additions or improvements.
    - **PATCH:** Backwards-compatible bug fixes or security patches.

- **VERSION File:**  
  The current version of the main branch is tracked in the `VERSION` file (e.g., `0.2.0`).

- **Maintenance Branches:**  
  Older versions are maintained in dedicated branches (e.g., `0.1.0-maintenance`). These branches allow for critical bug fixes and security patches to be applied without affecting ongoing development in the main branch.

---

## Safe Migration of Jobs

- **Parallel Job Versions:**  
  Multiple versions of the same job can coexist, allowing teams to migrate incrementally. For example, `jobs/v0_1_0/my_job.py` and `jobs/v0_2_0/my_job.py` can both be deployed and referenced independently.

- **Dependency Isolation:**  
  Downstream systems (e.g., Airflow DAGs, Glue jobs) can explicitly reference the required job version, ensuring that migrations do not break existing dependencies.

- **Gradual Adoption:**  
  New features or breaking changes can be rolled out to a subset of jobs or environments, while others continue to use the stable maintenance branch.

---

## Example: Versioned Job Migration Workflow

Suppose the main branch is at version `0.2.0` and you have a maintenance branch `0.1.0-maintenance`:

1. **Bug Fix on Maintenance Branch:**
    - A critical bug is discovered in a job running on `0.1.0`.
    - Apply the fix to the `0.1.0-maintenance` branch and release a new patch (e.g., `0.1.1`).
    - Downstream systems using `0.1.0` can upgrade to `0.1.1` without adopting new features or breaking changes from `0.2.0`.

2. **Developing New Features:**
    - New features and breaking changes are developed on the main branch (`0.2.0`).
    - Jobs and DAGs that are ready to adopt the new version can be updated to reference `0.2.0`.

3. **Coexistence:**
    - Both `0.1.x` and `0.2.x` jobs can be deployed and executed in parallel.
    - Each environment or workflow can independently choose when to migrate.

4. **Explicit Version Reference in Airflow DAG:**
    ```python
    # Example: Airflow DAG referencing a specific job version
    from dwh.jobs.v0_1_0.my_job import MyJob as MyJobV1
    from dwh.jobs.v0_2_0.my_job import MyJob as MyJobV2

    # Use MyJobV1 for legacy workflows
    legacy_task = PythonOperator(
        task_id='legacy_job',
        python_callable=MyJobV1().run,
        ...
    )

    # Use MyJobV2 for new workflows
    new_task = PythonOperator(
        task_id='new_job',
        python_callable=MyJobV2().run,
        ...
    )
    ```

---

## Benefits

- **Stability:**  
  Existing workflows are not disrupted by new releases or breaking changes.
- **Flexibility:**  
  Teams can migrate at their own pace, testing new versions before full adoption.
- **Security:**  
  Maintenance branches allow for rapid patching of critical issues without forcing upgrades.

---

## Best Practices

- Always update the `VERSION` file when releasing a new version.
- Use clear branch naming conventions for maintenance (e.g., `0.1.0-maintenance`).
- Document breaking changes and migration steps in release notes.
- Encourage downstream consumers to explicitly reference job versions.

---

