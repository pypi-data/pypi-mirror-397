from typing import Dict, Any

from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService, SparkJdbcService, \
    DirectJdbcService


class JdbcConnectionServiceFactory:
    """Factory for creating JDBC connections with various configuration options."""

    @staticmethod
    def create_connection(config: Dict[str, Any], spark_session=None) -> JdbcConnectionService:
        """
        Create a database connection service based on configuration.

        Config options:
        - database_type: Type of database (POSTGRES, MYSQL, etc.)
        - force_direct_connection: Force direct JDBC even with Spark available

        Connection details can be provided via:
        - jdbc_url: Direct JDBC URL
        - glue_connection_name + region: AWS Glue Connection
        - secret_name + region: AWS Secrets Manager
        - ssm_parameter + region: AWS Parameter Store
        - host, port, database, user, password: Direct parameters
        """
        print("JdbcConnectionService Configuration:", config)

        # Get connection details based on provided config
        connection_details = JdbcConnectionServiceFactory._resolve_connection_details(config)

        # Determine if we should use Spark or direct connection
        use_spark = (
            spark_session is not None
            and not config.get('force_direct_connection', False)
        )

        if use_spark:
            return SparkJdbcService(
                database_type=connection_details['database_type'],
                connection_details=connection_details,
                spark_session=spark_session
            )
        else:
            return DirectJdbcService(
                database_type=connection_details['database_type'],
                connection_details=connection_details
            )

    @staticmethod
    def _resolve_connection_details(config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve connection details from various sources."""
        # Database type is required
        if 'database_type' not in config:
            raise ValueError("database_type is required")

        database_type = config['database_type'].upper()

        # Start with empty connection details
        connection_details = {'database_type': database_type}

        # Resolve from Glue Connection
        if 'glue_connection_name' in config:
            glue_details = JdbcConnectionServiceFactory._get_glue_connection_details(
                config['glue_connection_name'],
                config.get('region', 'us-west-2')
            )
            connection_details.update(glue_details)

        # Resolve from Secrets Manager
        elif 'secret_name' in config:
            secret_details = JdbcConnectionServiceFactory._get_secrets_manager_details(
                config['secret_name'],
                config.get('region', 'us-west-2')
            )
            connection_details.update(secret_details)

        # Resolve from SSM Parameter Store
        elif 'ssm_parameter' in config:
            ssm_details = JdbcConnectionServiceFactory._get_ssm_parameter_details(
                config['ssm_parameter'],
                config.get('region', 'us-west-2')
            )
            connection_details.update(ssm_details)

        # Use direct JDBC URL if provided
        elif 'jdbc_url' in config:
            connection_details['jdbc_url'] = config['jdbc_url']
            # Add credentials if provided
            if 'user' in config:
                connection_details['user'] = config['user']
            if 'password' in config:
                connection_details['password'] = config['password']

        # Use direct parameters
        else:
            for param in ['host', 'port', 'database', 'user', 'password', 'database_path']:
                if param in config:
                    connection_details[param] = config[param]

        return connection_details

    @staticmethod
    def _get_glue_connection_details(connection_name: str, region: str) -> Dict[str, Any]:
        """Get connection details from AWS Glue Connection."""
        import boto3

        glue = boto3.client('glue', region_name=region)
        response = glue.get_connection(Name=connection_name)
        conn_props = response['Connection']['ConnectionProperties']

        # Extract connection details from JDBC URL
        jdbc_url = conn_props['JDBC_CONNECTION_URL']
        connection_details = {
            'jdbc_url': jdbc_url,
            'user': conn_props.get('USERNAME', ''),
            'password': conn_props.get('PASSWORD', '')
        }

        return connection_details

    @staticmethod
    def _get_secrets_manager_details(secret_name: str, region: str) -> Dict[str, Any]:
        """Get connection details from AWS Secrets Manager."""
        import boto3
        import json

        client = boto3.client('secretsmanager', region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])

    @staticmethod
    def _get_ssm_parameter_details(parameter_name: str, region: str) -> Dict[str, Any]:
        """Get connection details from AWS SSM Parameter Store."""
        import boto3
        import json

        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return json.loads(response['Parameter']['Value'])
