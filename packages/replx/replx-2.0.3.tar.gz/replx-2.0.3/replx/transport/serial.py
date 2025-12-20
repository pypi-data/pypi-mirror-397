"""Serial (USB/UART) transport implementation."""

from .base import Transport
from ..exceptions import TransportError

# Import pyserial
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    raise ImportError("pyserial is required. Install with: pip install pyserial")


class SerialTransport(Transport):
    """Serial (USB/UART) transport implementation using pyserial.
    
    Provides reliable cross-platform serial communication for MicroPython devices.
    """
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize serial connection using pyserial.
        
        :param port: Serial port name (e.g., COM3, /dev/ttyUSB0)
        :param baudrate: Baud rate (default: 115200)
        :param timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self._default_timeout = timeout
        self._serial = None
        
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            # Increase buffer size for better performance
            try:
                self._serial.set_buffer_size(rx_size=262144, tx_size=65536)
            except Exception:
                pass  # Not all platforms support this
        except serial.SerialException as e:
            raise TransportError(f"Failed to open serial port {port}: {e}") from e
    
    def write(self, data: bytes) -> int:
        """Write data to serial port."""
        try:
            return self._serial.write(data)
        except serial.SerialException as e:
            raise TransportError(f"Serial write error: {e}") from e
    
    def read(self, size: int = 1) -> bytes:
        """Read data from serial port."""
        try:
            return self._serial.read(size)
        except serial.SerialException as e:
            raise TransportError(f"Serial read error: {e}") from e
    
    def read_byte(self, timeout: float = None) -> bytes:
        """
        Read exactly 1 byte from serial port (blocking with timeout).
        
        :param timeout: Read timeout in seconds. None uses default timeout.
        :return: Single byte or empty bytes on timeout
        """
        try:
            if timeout is not None:
                old_timeout = self._serial.timeout
                self._serial.timeout = timeout
                try:
                    return self._serial.read(1)
                finally:
                    self._serial.timeout = old_timeout
            return self._serial.read(1)
        except serial.SerialException as e:
            raise TransportError(f"Serial read_byte error: {e}") from e
    
    def read_available(self) -> bytes:
        """
        Non-blocking read - returns immediately with available data or empty bytes.
        
        :return: Available bytes or empty if no data
        """
        try:
            waiting = self._serial.in_waiting
            if waiting > 0:
                return self._serial.read(waiting)
            return b""
        except serial.SerialException as e:
            error_msg = str(e).lower()
            if "clearcommerror" in error_msg or "not exist" in error_msg or "cannot find" in error_msg:
                raise TransportError(f"Serial port disconnected (device removed or cable unplugged)") from e
            raise TransportError(f"Serial read_available error: {e}") from e
    
    def read_all(self) -> bytes:
        """Read all available data from serial port."""
        return self.read_available()
    
    def in_waiting(self) -> int:
        """Return number of bytes in serial input buffer."""
        try:
            return self._serial.in_waiting
        except Exception:
            return 0
    
    def close(self) -> None:
        """Close serial port."""
        if self._serial and self._serial.is_open:
            self._serial.close()
    
    def reset_input_buffer(self) -> None:
        """Clear serial input buffer."""
        if self._serial:
            self._serial.reset_input_buffer()
    
    def reset_output_buffer(self) -> None:
        """Clear serial output buffer."""
        if self._serial:
            self._serial.reset_output_buffer()
    
    def check_connection(self) -> bool:
        """Check if serial connection is still alive.
        
        Returns True if connection is healthy, False if disconnected.
        """
        try:
            return self._serial.is_open if self._serial else False
        except Exception:
            return False
    
    def keep_alive(self) -> None:
        """Send keep-alive signal to prevent USB timeout.
        
        Note: For pyserial, checking in_waiting serves as keep-alive.
        """
        try:
            _ = self._serial.in_waiting
        except Exception:
            pass
    
    @property
    def is_open(self) -> bool:
        """Check if serial port is open."""
        return self._serial.is_open if self._serial else False
