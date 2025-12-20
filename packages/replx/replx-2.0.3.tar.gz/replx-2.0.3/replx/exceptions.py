"""Exception hierarchy for replx."""


class ReplxException(Exception):
    """Base exception for all replx operations."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class TransportError(ReplxException):
    """Base exception for transport-layer communication errors."""
    pass


class SerialError(TransportError):
    """Exception for Serial (USB/UART) transport errors."""
    pass


class WebREPLError(TransportError):
    """Exception for WebREPL (WebSocket) transport errors."""
    pass


class ProtocolError(ReplxException):
    """Base exception for MicroPython REPL protocol errors."""
    pass


class RawReplError(ProtocolError):
    """Exception for RAW REPL mode entry/exit errors."""
    pass


class RawPasteError(ProtocolError):
    """Exception for Raw-Paste mode errors."""
    pass


class ExecutionError(ProtocolError):
    """Exception for code execution errors on device."""
    pass


class FileSystemError(ReplxException):
    """Base exception for device filesystem operations."""
    pass


class DownloadError(FileSystemError):
    """Exception for file download errors."""
    pass


class UploadError(FileSystemError):
    """Exception for file upload errors."""
    pass


class CLIError(ReplxException):
    """Base exception for CLI/application-layer errors."""
    pass


class ValidationError(CLIError):
    """Exception for input validation errors."""
    pass


class CompilationError(CLIError):
    """Exception for mpy-cross compilation errors."""
    pass
