from typing import Dict, Any
from dwh.services.schema.schema_service import SchemaService, DDLSchemaService
from dwh.services.file.ddl_file_reader_factory import DDLFileReaderFactory


class SchemaServiceFactory:
    """Factory for creating schema services"""
    
    @staticmethod
    def create_schema_service(config: Dict[str, Any]) -> SchemaService:
        """
        Create a schema service based on configuration.
        
        Args:
            config: Configuration dictionary containing:
                - ddl_reader: "FS" or "S3"
                - For FS: base_path
                - For S3: region, bucket, prefix
            
        Returns:
            Configured DDLSchemaService instance
        """
        file_reader = DDLFileReaderFactory.create_ddl_file_reader(config)
        return DDLSchemaService(file_reader)
