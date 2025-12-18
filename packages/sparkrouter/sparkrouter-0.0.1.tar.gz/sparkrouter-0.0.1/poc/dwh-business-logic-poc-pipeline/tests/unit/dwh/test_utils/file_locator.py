from dwh.services.file.file_locator import FileLocator


class DummyFileLocator(FileLocator):
    """A dummy file locator for testing."""

    def __init__(self, files, file_contents=None):
        self._files = files
        self._file_contents = file_contents or {}

    def list_files(self, path):
        return self._files

    def read_file(self, file_path):
        return self._file_contents.get(file_path, "-- dummy sql --")
