from typing import Dict, Any

from dwh.services.file.ddl_file_reader import DDLFileReader, LocalDDLFileReader, S3DDLFileReader


class DDLFileReaderFactory:
    """Factory for creating DDL file readers"""
    
    VALID_TYPES = ['FS', 'S3']

    @staticmethod
    def _get_service_type(config: Dict[str, Any]) -> str:
        type = config.get('ddl_reader')
        if not type:
            raise ValueError(
                f"Missing ddl_reader. Valid options are: {', '.join(DDLFileReaderFactory.VALID_TYPES)}")
        type = type.strip().upper()
        return type    
    
    @staticmethod
    def create_ddl_file_reader(config: Dict[str, Any]) -> DDLFileReader:
        """Create a standard DDL file reader"""
        print("DDLFileReader Configuration:", config)
        type = DDLFileReaderFactory._get_service_type(config=config)
        if type == 'FS':
            base_path = config.get('base_path')
            if not base_path:
                raise ValueError("base_path is required when using FS ddl filereader")
            return LocalDDLFileReader(base_path=base_path)
        elif type == 'S3':
            s3_region = config.get('region')
            if not s3_region:
                raise ValueError("region is required when using S3 ddl filereader")
            bucket = config.get('bucket')
            if not bucket:
                raise ValueError("bucket is required when using S3 ddl filereader")
            prefix = config.get('prefix')
            if prefix is None:
                raise ValueError("prefix is required, even if blank, when using S3 ddl filereader")
            endpoint_url = config.get('endpoint_url')
            aws_access_key_id = config.get('aws_access_key_id')
            aws_secret_access_key = config.get('aws_secret_access_key')
            return S3DDLFileReader(
                region=s3_region, 
                bucket=bucket, 
                prefix=prefix,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        else:
            raise ValueError(
                f"Unsupported ddl_reader[{type}]. Valid options are: {', '.join(DDLFileReaderFactory.VALID_TYPES)}")
