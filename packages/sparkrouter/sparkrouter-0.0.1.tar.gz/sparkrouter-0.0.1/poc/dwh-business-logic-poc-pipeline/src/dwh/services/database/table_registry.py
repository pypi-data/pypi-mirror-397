from pyspark.sql import DataFrame, SparkSession


class TableRegistry:
    """
    Handles registration of tables as views in Spark's catalog.
    
    This class encapsulates the logic for registering tables with different naming conventions,
    allowing for consistent table name handling across the application.
    """
    
    @staticmethod
    def register_table(df: DataFrame, source_table: str) -> None:
        """
        Register a DataFrame as a view in Spark's catalog with appropriate naming conventions.
        
        Args:
            df: DataFrame to register
            source_table: Original table name (can include schema qualification and quotes)
        """
        # Clean table name by removing quotes and other invalid characters for Spark views
        clean_table_name = source_table.strip('"').strip("'")
        
        # Register the table in Spark's catalog for SQL queries
        # We need to handle schema-qualified names (e.g., "schema.table")
        if '.' in clean_table_name:
            schema, table = clean_table_name.split('.', 1)  # Split only on first dot
            # Register with fully qualified name (replacing . with _)
            qualified_view_name = clean_table_name.replace('.', '_')
            df.createOrReplaceTempView(qualified_view_name)
            print(f"Registered table '{source_table}' as view '{qualified_view_name}'")
            
            # Also register with just the table name for convenience
            try:
                df.createOrReplaceTempView(table)
                print(f"Also registered as '{table}'")
            except Exception as e:
                print(f"Note: Could not create simple view: {e}")
                
            # Register with dl_schema_table format for backward compatibility
            # This is needed for tests that use this format
            if schema.startswith('dl_'):
                try:
                    dl_view_name = f"dl_{schema.replace('dl_', '')}_{table}"
                    df.createOrReplaceTempView(dl_view_name)
                    print(f"Also registered as '{dl_view_name}' for backward compatibility")
                except Exception as e:
                    print(f"Note: Could not create dl_schema_table view: {e}")
        else:
            # No schema qualification, just register as is (cleaned)
            df.createOrReplaceTempView(clean_table_name)
            print(f"Registered table '{source_table}' as view '{clean_table_name}'")
    
    @staticmethod
    def unregister_table(spark: SparkSession, table_name: str) -> None:
        """
        Unregister a table view from Spark's catalog.
        
        Args:
            spark: SparkSession to use
            table_name: Table name to unregister
        """
        try:
            spark.catalog.dropTempView(table_name)
            print(f"Dropped view '{table_name}'")
        except Exception:
            # View doesn't exist or other error - ignore
            pass
    
    @staticmethod
    def get_view_names(table_name: str) -> list:
        """
        Get all possible view names for a table.
        
        Args:
            table_name: Original table name
            
        Returns:
            List of possible view names
        """
        # Clean table name by removing quotes
        clean_table_name = table_name.strip('"').strip("'")
        view_names = [clean_table_name]
        
        if '.' in clean_table_name:
            schema, table = clean_table_name.split('.', 1)  # Split only on first dot
            # Add qualified name (replacing . with _)
            view_names.append(clean_table_name.replace('.', '_'))
            # Add just the table name
            view_names.append(table)
            # Add dl_schema_table format for backward compatibility
            if schema.startswith('dl_'):
                view_names.append(f"dl_{schema.replace('dl_', '')}_{table}")
                
        return view_names
