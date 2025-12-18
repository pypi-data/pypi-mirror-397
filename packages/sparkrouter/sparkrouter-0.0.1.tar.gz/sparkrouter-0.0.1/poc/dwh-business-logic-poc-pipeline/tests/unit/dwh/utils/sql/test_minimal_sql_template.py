from dwh.utils.sql.named_parameter_sql import NamedParameterSQLTemplate

def test_minimal_sql_template():
    """Test a minimal SQL template with the created_by parameter."""
    
    # Create a simple SQL script with the created_by parameter
    sql = ":created_by AS created_by"
    
    # Create the template
    template = NamedParameterSQLTemplate(sql)
    
    # Print the parameters found in the SQL
    print("Parameters found in SQL:")
    for param in template.params_map.keys():
        print(f"  - {param}")
    
    # Create parameters dict with the created_by parameter
    params = {'created_by': 'test_user'}
    
    # Try to format the SQL
    try:
        formatted_sql = template.format(params)
        print(f"\nFormatted SQL: {formatted_sql}")
    except ValueError as e:
        print(f"\nError: {e}")
    
    # Try with a different parameter name
    sql2 = ":createdBy AS created_by"
    template2 = NamedParameterSQLTemplate(sql2)
    
    print("\nParameters found in SQL2:")
    for param in template2.params_map.keys():
        print(f"  - {param}")
    
    # Try to format with the wrong parameter name
    try:
        formatted_sql2 = template2.format(params)
        print(f"\nFormatted SQL2: {formatted_sql2}")
    except ValueError as e:
        print(f"\nExpected error: {e}")
    
    # Try with the correct parameter name
    params2 = {'createdBy': 'test_user'}
    try:
        formatted_sql2 = template2.format(params2)
        print(f"\nFormatted SQL2 with correct param: {formatted_sql2}")
    except ValueError as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_minimal_sql_template()