from abc import ABC, abstractmethod


class FileLocator(ABC):

    @abstractmethod
    def list_files(self, path, file_extension=None) -> list[str]:
        """
        Abstract method to get the file path for a given schema and filename.
        """
        pass

    @abstractmethod
    def read_file(self, file_path) -> str:
        """
        Abstract method to read the contents of a file.
        """
        pass


class FSFileLocator(FileLocator):

    def __init__(self, root_path):
        self.root_path = root_path

    def list_files(self, path, file_extension=None) -> list[str]:
        """
        List all files in the specified path.

        Args:
            path (str): The directory path to list files from.
            file_extension (str, optional): File extension to filter by. If None, returns all files.
        Returns:
            list: A list of file paths in the specified directory.
        """
        import os
        full_path = os.path.join(self.root_path, path)
        files = os.listdir(full_path)
        if file_extension is not None:
            # Filter by extension if provided
            files = [f for f in files if f.endswith(file_extension)]

        # Return relative path to root
        return [os.path.join(path, f).replace(os.sep, "/") for f in files]

    def read_file(self, file_path):
        """
        Read the contents of a file.

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: The contents of the file.
        """
        import os
        full_path = os.path.join(self.root_path, file_path)

        with open(full_path, 'r', encoding='utf-8') as file:
            return file.read()


class S3FileLocator(FileLocator):

    def __init__(self, s3_bucket: str, s3_prefix: str, region: str):
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix

        import boto3
        self.s3 = boto3.client('s3', region_name=region)

    def list_files(self, path, file_extension=None):
        """
        List all files in the specified S3 path.

        Args:
            path (str): The S3 path to list files from.
            file_extension (str, optional): File extension to filter by. If None, returns all files.
        Returns:
            list: A list of file keys in the specified S3 path.
        """
        s3_path = f"{self.s3_prefix}/{path}" if path else self.s3_prefix
        s3_path = s3_path.replace('\\', '/')
        if s3_path and not s3_path.endswith('/'):
            s3_path = s3_path + '/'

        print(f"Listing files in s3://{self.s3_bucket}/{s3_path}, file_extension: {file_extension}")

        response = self.s3.list_objects_v2(Bucket=self.s3_bucket, Prefix=s3_path)

        files = []
        for obj in response.get('Contents', []):
            key = obj['Key']

            # Apply file extension filter if specified
            if file_extension and not key.endswith(file_extension):
                continue

            # Only include files in the specified path
            if key.startswith(s3_path):
                # Convert to path relative to the S3 prefix and normalize to forward slashes
                relative_key = key[len(self.s3_prefix):].lstrip('/').replace('\\', '/')
                files.append(relative_key)

        print(f"Found {len(files)} files in s3://{self.s3_bucket}/{s3_path}")

        return files

    def read_file(self, file_path):
        """
        Read the contents of a file from S3.

        Args:
            file_path (str): The S3 key of the file to read.

        Returns:
            str: The contents of the file.
        """
        s3_key = f"{self.s3_prefix}/{file_path}".replace('//', '/')

        obj = self.s3.get_object(Bucket=self.s3_bucket, Key=s3_key)
        return obj['Body'].read().decode('utf-8')
