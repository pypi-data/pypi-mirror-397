from abc import ABC, abstractmethod

class BaseStorage(ABC):
    """
    Base interface for all storage backends.
    Every storage provider must implement these methods.
    """

    @abstractmethod
    def upload(self, filepath, filename=None, **kwargs):
        pass

    @abstractmethod
    def delete(self, filename):
        pass

    @abstractmethod
    def generate_url(self, filename, expires=3600):
        pass

    @abstractmethod
    def list_files(self, prefix="", **kwargs):
        pass

    @abstractmethod
    def sync_folder(self, local_folder, mode="push", delete=False):
        pass
