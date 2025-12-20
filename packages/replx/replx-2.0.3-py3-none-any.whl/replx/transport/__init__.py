"""Transport layer package for replx."""

from .base import Transport

# Lazy imports for transport implementations
_SerialTransport = None
_WebREPLTransport = None


def _get_serial_transport():
    """Lazy import SerialTransport only when needed."""
    global _SerialTransport
    if _SerialTransport is None:
        from .serial import SerialTransport
        _SerialTransport = SerialTransport
    return _SerialTransport


def _get_webrepl_transport():
    """Lazy import WebREPLTransport only when needed."""
    global _WebREPLTransport
    if _WebREPLTransport is None:
        from .webrepl import WebREPLTransport
        _WebREPLTransport = WebREPLTransport
    return _WebREPLTransport


def create_transport(connection_string: str, baudrate: int = 115200, password: str = "", timeout: float = 1.0) -> Transport:
    """
    Factory function to create appropriate transport.
    Uses lazy loading - only imports the transport module actually needed.
    
    :param connection_string: Either serial port (COM3, /dev/ttyUSB0) or WebREPL URL (ws://192.168.4.1:8266)
    :param baudrate: Baud rate for serial connections
    :param password: Password for WebREPL connections
    :param timeout: Connection timeout in seconds (WebREPL only)
    :return: Transport instance
    """
    if connection_string.startswith("ws://") or connection_string.startswith("wss://"):
        # Parse WebREPL URL and create WebREPL transport
        from urllib.parse import urlparse
        parsed = urlparse(connection_string)
        host = parsed.hostname or "192.168.4.1"
        port = parsed.port or 8266
        
        WebREPLTransport = _get_webrepl_transport()
        return WebREPLTransport(host=host, port=port, password=password, timeout=timeout)
    else:
        # Create Serial transport
        SerialTransport = _get_serial_transport()
        return SerialTransport(port=connection_string, baudrate=baudrate)


# Export public API
__all__ = [
    'Transport',
    'create_transport',
]
