from typing import Dict, Any

from dwh.services.file.file_locator import FileLocator, S3FileLocator, FSFileLocator


class FileLocatorFactory:

    @staticmethod
    def _get_service_type(config: Dict[str, Any]) -> str:
        type = config.get('file_service')
        if not type:
            valid_types = ['S3', 'FS']
            raise ValueError(
                f"Missing file locator_type. Valid options are: {', '.join(valid_types)}")

        type = type.strip().upper()

        return type

    @staticmethod
    def create_file_locator(config: Dict[str, Any]) -> FileLocator:
        """
        Factory method to get the appropriate email service based on the configuration.
        :param kwargs: Configuration parameters for the email service.
        :return: An instance of the email service.
        """
        print("FileLocator Configuration:", config)

        type = FileLocatorFactory._get_service_type(config)
        if type == 'S3':
            s3_region = config.get('region')
            if not s3_region:
                raise ValueError("s3_region is required for S3FileLocator")
            bucket = config.get('bucket_name')
            prefix = config.get('prefix', '')

            if not bucket:
                raise ValueError("bucket_name is required for S3FileLocator")

            return S3FileLocator(
                s3_bucket=bucket,
                s3_prefix=prefix,
                region=s3_region,
            )
        elif type == 'FS':
            root_path = config.get('root_path', None)
            if root_path is None:
                raise ValueError("root_path is required for FSFileLocator")
            return FSFileLocator(
                root_path=root_path,
            )
        else:
            valid_types = ['S3', 'FS']
            raise ValueError(f"Unsupported file locator_type[{type}]. Valid options are: {', '.join(valid_types)}")
