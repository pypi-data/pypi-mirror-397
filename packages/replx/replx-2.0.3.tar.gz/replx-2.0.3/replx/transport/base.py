"""Transport abstraction layer - Base classes."""

from abc import ABC, abstractmethod


class Transport(ABC):
    """Abstract base class for device communication."""
    
    @abstractmethod
    def write(self, data: bytes) -> int:
        """Write data to the device."""
        pass
    
    @abstractmethod
    def read(self, size: int = 1) -> bytes:
        """Read data from the device."""
        pass
    
    def read_byte(self, timeout: float = None) -> bytes:
        """
        Read exactly 1 byte (blocking with timeout).
        Follows pyboard.py pattern for reliable streaming.
        Default implementation uses read(1).
        
        :param timeout: Read timeout in seconds. None uses default.
        :return: Single byte or empty bytes on timeout
        """
        return self.read(1)
    
    @abstractmethod
    def read_available(self, timeout_ms: int = 10) -> bytes:
        """
        Non-blocking read with timeout.
        Returns immediately with available data or empty bytes after timeout.
        
        :param timeout_ms: Timeout in milliseconds
        :return: Available bytes or empty if no data
        """
        pass
    
    @abstractmethod
    def read_all(self) -> bytes:
        """Read all available data."""
        pass
    
    @abstractmethod
    def in_waiting(self) -> int:
        """Return number of bytes waiting to be read."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the connection."""
        pass
    
    @abstractmethod
    def reset_input_buffer(self) -> None:
        """Clear input buffer."""
        pass
    
    @abstractmethod
    def reset_output_buffer(self) -> None:
        """Clear output buffer."""
        pass
    
    @property
    @abstractmethod
    def is_open(self) -> bool:
        """Check if connection is open."""
        pass
