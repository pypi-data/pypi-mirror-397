import os
import re
from abc import ABC, abstractmethod


class DDLFileReader(ABC):
    """Reads and parses DDL files"""
    
    @abstractmethod
    def read_ddl_file(self, file_path: str) -> str:
        """Read DDL file content"""
        pass
        
    def extract_table_name(self, ddl_content: str) -> str:
        """Extract table name from DDL content"""
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:(\w+)\.)?(\w+)'
        match = re.search(pattern, ddl_content, re.IGNORECASE)

        if match:
            schema = match.group(1)
            table = match.group(2)
            return f"{schema}.{table}" if schema else table

        raise ValueError("Could not extract table name from DDL")

    
class S3DDLFileReader(DDLFileReader):

    def __init__(self, region: str, bucket: str, prefix: str, endpoint_url: str = None, aws_access_key_id: str = None, aws_secret_access_key: str = None):
        import boto3
        self.bucket = bucket
        self.prefix = prefix
        
        client_kwargs = {'region_name': region}
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url
        if aws_access_key_id:
            client_kwargs['aws_access_key_id'] = aws_access_key_id
        if aws_secret_access_key:
            client_kwargs['aws_secret_access_key'] = aws_secret_access_key
            
        self.s3_client = boto3.client('s3', **client_kwargs)        
    
    def read_ddl_file(self, file_path: str) -> str:
        try:
            prefix = self.prefix.rstrip('/')
            if prefix:
                path = f"{prefix}/{file_path}" if not file_path.startswith(prefix) else file_path
            else:
                path = file_path
            response = self.s3_client.get_object(Bucket=self.bucket, Key=path)
            return response['Body'].read().decode('utf-8')
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"DDL file not found in S3: s3://{self.bucket}/{file_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to read DDL file from S3: s3://{self.bucket}/{file_path}") from e
        
        
class LocalDDLFileReader(DDLFileReader):
    
    def __init__(self, base_path: str):
        self.base_path = base_path
    
    def read_ddl_file(self, file_path: str) -> str:
        """Read DDL file content"""
        full_path = os.path.join(self.base_path, file_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"DDL file not found: {full_path}")

        with open(full_path, 'r') as file:
            return file.read()


class FSDDLFileReader(DDLFileReader):
    
    def __init__(self, base_path: str):
        self.base_path = base_path
    
    def read_ddl_file(self, file_path: str) -> str:
        """Read DDL file content"""
        full_path = os.path.join(self.base_path, file_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"DDL file not found: {full_path}")

        with open(full_path, 'r') as file:
            return file.read()
