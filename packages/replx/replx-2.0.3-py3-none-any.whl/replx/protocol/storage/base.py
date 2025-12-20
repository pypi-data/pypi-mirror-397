"""Abstract base class for device storage operations."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple


class DeviceStorage(ABC):
    """Abstract base class for device storage operations."""
    
    def __init__(self, repl_protocol, core: str = "RP2350", device: str = "", device_root_fs: str = "/"):
        """Initialize storage manager."""
        self.repl = repl_protocol
        self.core = core
        self.device = device
        self.device_root_fs = device_root_fs
    
    @abstractmethod
    def get(self, remote: str, local: str = None) -> bytes:
        """
        Download a file from the device.
        
        :param remote: Remote file path on device
        :param local: Local path to save file (None = return bytes)
        :return: File content as bytes (if local is None)
        """
        pass
    
    @abstractmethod
    def put(self, local: str, remote: str, progress_callback=None):
        """
        Upload a file to the device.
        
        :param local: Local file path
        :param remote: Remote path on device
        :param progress_callback: Optional progress callback(bytes_sent, total_bytes)
        """
        pass
    
    @abstractmethod
    def ls(self, path: str = "/") -> List[str]:
        """
        List directory contents (names only).
        
        :param path: Directory path
        :return: List of filenames/directory names
        """
        pass
    
    @abstractmethod
    def ls_detailed(self, path: str = "/") -> List[list]:
        """
        List directory contents with detailed info.
        
        Returns list of [name, size, is_dir] entries.
        
        :param path: Directory path
        :return: List of [filename, size, is_directory]
        """
        pass
    
    @abstractmethod
    def ls_recursive(self, path: str = "/") -> List[dict]:
        """
        Recursively list directory contents.
        
        :param path: Starting directory path
        :return: List of file info dicts with path, size, is_dir
        """
        pass
    
    @abstractmethod
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""
        pass
    
    @abstractmethod
    def state(self, path: str) -> int:
        """Get file size or stat info."""
        pass
    
    @abstractmethod
    def mkdir(self, path: str) -> bool:
        """Create directory."""
        pass
    
    @abstractmethod
    def rm(self, path: str):
        """Remove file."""
        pass
    
    @abstractmethod
    def rmdir(self, path: str):
        """Remove directory."""
        pass
    
    @abstractmethod
    def mem(self) -> Tuple[int, int, int, float]:
        """Get device memory info (allocated, free, total, %)."""
        pass
