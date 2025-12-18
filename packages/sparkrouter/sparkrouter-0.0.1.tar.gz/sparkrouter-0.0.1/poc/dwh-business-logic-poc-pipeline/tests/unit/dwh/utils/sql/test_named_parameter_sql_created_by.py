import unittest
from dwh.utils.sql import named_parameter_sql

class TestNamedParameterSQL(unittest.TestCase):
    
    def test_missing_created_by_parameter(self):
        """Test to reproduce the 'Missing parameter: created_by' error."""
        # Create a SQL script with :created_by parameter
        sql = """
        SELECT 
            column1,
            column2,
            :created_by AS created_by
        FROM 
            some_table
        WHERE 
            date BETWEEN :start_date AND :end_date
        """
        
        # Create the template
        template = named_parameter_sql.NamedParameterSQLTemplate(sql)
        
        # Print the parameters found in the SQL
        print("Parameters found in SQL:")
        for param in template.params_map.keys():
            print(f"  - {param}")
        
        # Create parameters dict with all required parameters
        params = {
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'created_by': 'test_user'
        }
        
        # Print the parameters being passed
        print("\nParameters being passed:")
        for key, value in params.items():
            print(f"  - {key}: {value}")
        
        # This should work
        try:
            formatted_sql = template.format(params)
            print("\nFormatted SQL (should work):")
            print(formatted_sql)
        except ValueError as e:
            print(f"\nError (should not happen): {e}")
        
        # Now try with missing created_by parameter
        params_missing = {
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        }
        
        # This should fail with "Missing parameter: created_by"
        try:
            formatted_sql = template.format(params_missing)
            print("\nFormatted SQL (should fail but didn't):")
            print(formatted_sql)
        except ValueError as e:
            print(f"\nExpected error: {e}")
        
        # Now try with empty string for created_by
        params_empty = {
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'created_by': ''
        }
        
        # This should work
        try:
            formatted_sql = template.format(params_empty)
            print("\nFormatted SQL with empty created_by (should work):")
            print(formatted_sql)
        except ValueError as e:
            print(f"\nError with empty created_by (should not happen): {e}")

if __name__ == '__main__':
    unittest.main()