# Design Decisions

This document captures key design decisions made for the database services package.

## Table Name Handling in JDBC with Spark

### Problem
Spark SQL cannot directly query tables with schema-qualified names like 'schema.table'. This creates a leaky abstraction where users need to be aware of the transformation from `schema.table` to `schema_table` format.

### Solution
We implemented a three-component design:

1. **QueryExecutor**
   - High-level interface for executing SQL queries
   - Transforms SQL with schema.table references to schema_table format
   - Delegates to DataSourceStrategy for actual data operations

2. **DataSourceStrategy**
   - Defines interface for data source operations
   - Provides get_table_view_name() for table name transformation
   - Implemented by concrete strategies (JDBC, SparkSQL, Databricks)

3. **TableRegistry**
   - Centralizes table registration logic
   - Manages view naming conventions
   - Handles registration and unregistration of tables in Spark's catalog

### Benefits
- Users can write natural SQL without worrying about implementation details
- Separation of concerns between components
- Consistent table name handling across the application

### Alternatives Considered
1. **SQL Parser Approach**: Using a full SQL parser to transform queries. Rejected due to complexity and potential performance issues.
2. **Custom JDBC Driver**: Creating a custom JDBC driver that handles schema-qualified names. Rejected due to maintenance overhead.
3. **Requiring Modified SQL**: Requiring users to write SQL with schema_table format. Rejected as it creates a poor developer experience.

## Testing Approach

### Decision
All tests use Noop implementations rather than mocks, patches, or monkeypatching.

### Rationale
- Tests should verify actual behavior, not implementation details
- Noops provide predictable behavior without external dependencies
- This approach leads to more maintainable and less brittle tests