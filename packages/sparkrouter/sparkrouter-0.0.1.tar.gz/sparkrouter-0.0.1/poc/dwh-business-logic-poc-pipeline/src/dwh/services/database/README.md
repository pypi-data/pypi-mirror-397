# Database Services

This package provides abstractions for working with different database systems through a strategy pattern.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                           Client Code                                   │
│                                                                         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                │ uses
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                           QueryExecutor                                 │
│                                                                         │
│  - Transforms SQL queries with schema.table → schema_table              │
│  - Handles parameter substitution                                       │
│  - Delegates to DataSourceStrategy for data operations                  │
│                                                                         │
└─────────────┬─────────────────────────────────────┬─────────────────────┘
              │                                     │
              │ uses                                │ uses
              │                                     │
              ▼                                     ▼
┌─────────────────────────────┐     ┌─────────────────────────────────────┐
│                             │     │                                     │
│     DataSourceStrategy      │     │         TableRegistry               │
│     (Abstract Class)        │     │                                     │
│                             │     │  - Handles table registration       │
│  - get_source_df()          │     │  - Manages view naming conventions  │
│  - write_sink_df()          │     │  - Centralizes registration logic   │
│  - get_table_view_name()    │     │                                     │
│                             │     │                                     │
└─────────────┬───────────────┘     └─────────────────────────────────────┘
              │
              │ implements
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                      Concrete Strategies                                │
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │                 │    │                 │    │                 │      │
│  │ JDBCStrategy    │    │ SparkSQLStrategy│    │ DatabricksStrat.│      │
│  │                 │    │                 │    │                 │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### DataSourceStrategy

The `DataSourceStrategy` abstract class defines the interface for different data source strategies:

- `get_source_df`: Get a DataFrame for a source table
- `write_sink_df`: Write a DataFrame to a sink table
- `prepare`: Optional setup (e.g., USE SCHEMA)
- `postprocess`: Optional cleanup (e.g., VACUUM)
- `get_table_view_name`: Get the name to use in SQL queries for a table

Implementations include:
- `SparkSQLStrategy`: For Spark SQL tables
- `JDBCStrategy`: For JDBC connections
- `DatabricksStrategy`: For Databricks

### TableRegistry

The `TableRegistry` class centralizes table registration logic:

- Handles registration of tables as views in Spark's catalog
- Manages view naming conventions
- Provides consistent table name handling across the application

### QueryExecutor

The `QueryExecutor` class provides transparent table name resolution for SQL queries:

- Automatically handles schema-qualified table names (e.g., `schema.table`)
- Transforms table references to match the format required by the underlying strategy
- Allows users to write natural SQL without worrying about implementation details
- Uses DataSourceStrategy for actual data operations

## Data Flow

1. Client code creates a QueryExecutor with appropriate DataSourceStrategy
2. Client executes SQL query with natural schema.table syntax
3. QueryExecutor transforms SQL using strategy's get_table_view_name()
4. QueryExecutor delegates to DataSourceStrategy for data operations
5. DataSourceStrategy uses TableRegistry to register tables with appropriate naming

## JDBC Table Name Handling

Spark SQL cannot directly query tables with schema-qualified names like 'schema.table'. The solution handles this by:

1. Using original schema-qualified names (e.g., 'dl_stage.table') for JDBC operations
2. Registering tables as temporary views with modified names via TableRegistry
3. Transforming SQL queries to use the registered view names via QueryExecutor

## Example Usage

```python
# Create a QueryExecutor
query_executor = QueryExecutor(spark, jdbc_strategy)

# Execute a SQL query with natural schema.table syntax
sql = "SELECT * FROM schema.table WHERE date = :date"
params = {"date": "2023-01-01"}
result_df = query_executor.execute_sql(sql, params)
```


This approach allows users to write SQL using natural schema.table syntax without worrying about the underlying implementation details.