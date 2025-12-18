import os
from typing import Dict
from dwh.services.file.ddl_file_reader import DDLFileReader


class DDLFileReaderForTesting(DDLFileReader):
    """Test implementation of DDLFileReader that can handle test content and auto-locate files"""
    
    def __init__(self, file_contents: Dict[str, str] = None):
        self.file_contents = file_contents or {}
        self._business_logic_root = None
    
    def read_ddl_file(self, file_path: str) -> str:
        """Read DDL file content, supporting both real files and test content"""
        # If we have test content for this path, use it
        if file_path in self.file_contents:
            return self.file_contents[file_path]
        
        # Try to resolve relative paths from business logic root
        if not os.path.isabs(file_path):
            business_root = self._find_business_logic_root()
            full_path = os.path.join(business_root, file_path)
            if os.path.exists(full_path):
                file_path = full_path
        
        # Otherwise, read the real file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DDL file not found: {file_path}")
        
        with open(file_path, 'r') as file:
            return file.read()
    
    def _find_business_logic_root(self):
        """Find the business-logic root directory by looking for schemas folder"""
        if self._business_logic_root is not None:
            return self._business_logic_root
            
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
            schemas_dir = os.path.join(current_dir, 'schemas')
            if os.path.exists(schemas_dir) and os.path.isdir(schemas_dir):
                self._business_logic_root = current_dir
                return current_dir
            current_dir = os.path.dirname(current_dir)
        raise FileNotFoundError("Could not find business-logic root directory with schemas folder")