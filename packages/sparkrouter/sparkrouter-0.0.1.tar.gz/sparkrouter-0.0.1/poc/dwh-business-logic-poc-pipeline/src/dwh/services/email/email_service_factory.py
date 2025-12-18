from typing import Dict, Any
from dwh.services.email.email_service import SESEmailService, NoopEmailService, SMTPEmailService, EmailService


class EmailServiceFactory:
    """
    Factory class for creating instances of email services.
    
    The EmailServiceFactory implements the factory design pattern to create
    different types of email services based on configuration parameters.
    
    Currently supported email service types:
    - SES: Amazon Simple Email Service for sending emails through AWS
    - SMTP: Standard SMTP service for sending emails through a configured SMTP server
    - NOOP: No-operation service that logs messages but doesn't send actual emails
           (useful for testing or environments where emails should be disabled)
    
    Configuration is passed via a dictionary with the key 'email_service'.
    
    Example usage:
    ```python
    # Create an SES email service
    ses_config = {
        'email_service': {
            'service_type': 'SES',
            'region': 'us-west-1'
        }
    }
    email_service = EmailServiceFactory.create_email_service(**ses_config)
    
    # Create an SMTP email service with credential provider
    smtp_config = {
        'email_service': {
            'service_type': 'SMTP',
            'host': 'smtp.example.com',
            'port': 587
        },
        # Additional credential provider configuration is required
        # This will be passed to CredentialProviderFactory.create_credential_provider()
    }
    email_service = EmailServiceFactory.create_email_service(**smtp_config)
    
    # Create a NOOP email service
    noop_config = {
        'email_service': {
            'service_type': 'NOOP'
        }
    }
    email_service = EmailServiceFactory.create_email_service(**noop_config)
    ```
    """

    @staticmethod
    def _get_service_type(config: Dict[str, Any]) -> str:
        type = config.get('service_type')
        if not type:
            valid_types = ['SES', 'SMTP', 'NOOP']
            raise ValueError(f"Missing email service_type. Valid options are: {', '.join(valid_types)}")

        type = type.strip().upper()

        return type

    @staticmethod
    def create_email_service(config: Dict[str, Any]) -> EmailService:
        """
        Factory method to create the appropriate email service based on configuration.
        
        This method looks for a configuration parameter with the key 'email_service'.
        
        The configuration can be either a dictionary or a JSON string with the following structure:
        
        For SES email service:
        {
            'service_type': 'SES',           # Required: Must be 'SES' (case-insensitive)
            'region': 'us-west-1'            # Optional: AWS region (defaults to 'us-west-1')
        }
        
        For SMTP email service:
        {
            'service_type': 'SMTP',          # Required: Must be 'SMTP' (case-insensitive)
            'host': 'smtp.example.com',      # Optional: SMTP server (defaults to 'airdoor.internal.shutterfly.com')
            'port': 587                      # Optional: SMTP port (defaults to 25)
        }
        
        For SMTP service, credential provider configuration is also required.
        The same kwargs are passed to CredentialProviderFactory.create_credential_provider(),
        which is used to obtain authentication credentials for the SMTP server.
        See the CredentialProviderFactory documentation for details on configuring
        the credential provider.
        
        For NOOP email service:
        {
            'service_type': 'NOOP'           # Required: Must be 'NOOP' (case-insensitive)
        }
        
        Args:
            **kwargs: Dictionary containing the configuration parameters
        
        Returns:
            A concrete implementation of an email service (SESEmailService, SMTPEmailService, or NoopEmailService)
        
        Raises:
            ValueError: If required parameters are missing or invalid (service_type)
            ValueError: If an unsupported service_type is specified
            ValueError: If the JSON string cannot be parsed
            Any exceptions raised by CredentialProviderFactory.create_credential_provider()
        """
        print("EmailService Configuration:", config)

        type = EmailServiceFactory._get_service_type(config=config)
        if type == 'NOOP':
            return NoopEmailService()
        elif type == 'SES':
            ses_region = config.get('region')
            if ses_region is None:
                raise ValueError("ses_region is required for SESEmailService")
            return SESEmailService(region=ses_region)
        elif type == 'SMTP':
            smtp_server = config.get('host', 'airdoor.internal.shutterfly.com')
            smtp_port = config.get('port', 25)
            username = config.get('username')
            password = config.get('password')
            return SMTPEmailService(smtp_server=smtp_server, smtp_port=smtp_port, username=username, password=password)
        else:
            # List all available email service types
            valid_types = ['SES', 'SMTP', 'NOOP']
            raise ValueError(f"Unsupported email service_type[{type}]. Valid options are: {', '.join(valid_types)}")
