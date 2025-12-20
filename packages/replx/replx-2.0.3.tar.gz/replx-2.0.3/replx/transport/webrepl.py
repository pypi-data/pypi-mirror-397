"""WebREPL (WebSocket) transport implementation."""

import time
from typing import Optional

from .base import Transport
from ..exceptions import TransportError


class WebREPLTransport(Transport):
    """WebREPL (WebSocket) transport implementation."""
    
    def __init__(self, host: str, port: int = 8266, password: str = "", timeout: float = 1.0):
        """
        Initialize WebREPL connection.
        
        Follows MicroPython WebREPL protocol:
        1. WebSocket connect
        2. Receive "Welcome to MicroPython\r\n"
        3. If password enabled: receive "Password: " and authenticate
        4. Enter REPL mode (receive ">>> " prompt)
        
        :param host: Device IP address or hostname
        :param port: WebREPL port (default: 8266)
        :param password: WebREPL password (empty string = no password)
        :param timeout: Connection timeout in seconds
        """
        try:
            import websocket as ws
            self._websocket = ws
        except ImportError:
            raise ImportError(
                "websocket-client is required for WebREPL support. "
                "Install it with: pip install websocket-client"
            )
        
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self._ws: Optional[ws.WebSocket] = None
        self._buffer = bytearray()
        self._ws_timeout_exc = self._websocket.WebSocketTimeoutException
        
        # Connect to WebREPL
        url = f"ws://{host}:{port}"
        self._ws = ws.create_connection(url, timeout=timeout)
        
        # Complete WebREPL handshake
        self._handshake()
    
    def _handshake(self) -> None:
        """
        Complete WebREPL connection handshake.
        
        Actual protocol observed:
        1. Server sends: "Password: "
        2. Client sends: password + "\r\n"
        3. Server sends: "\r\nWebREPL connected\r\n>>> "
        
        Note: Server sends password prompt IMMEDIATELY, no welcome message.
        """
        try:
            self._ws.settimeout(self.timeout)
            
            # Step 1: Receive password prompt
            prompt = self._ws.recv()
            if isinstance(prompt, str):
                prompt = prompt.encode('utf-8')
            
            if b"Password:" not in prompt:
                raise ConnectionError(f"Expected 'Password:' prompt, got: {prompt!r}")
            
            # Step 2: Send password (or empty if no password)
            if self.password:
                password_line = (self.password + "\r\n").encode('utf-8')
            else:
                # If no password, still need to send something (empty line)
                password_line = b"\r\n"
            
            self._ws.send(password_line.decode('utf-8'))
            
            # Step 3: Receive authentication response (should include REPL prompt)
            auth_response = self._ws.recv()
            if isinstance(auth_response, str):
                auth_response = auth_response.encode('utf-8')
            
            # Check for access denied
            if b"Access denied" in auth_response or b"incorrect" in auth_response.lower():
                self.close()
                raise ConnectionError("WebREPL authentication failed: access denied")
            
            # Should contain the REPL prompt ">>> "
            if b">>>" not in auth_response and b">>>" not in auth_response:
                # Some devices might not send prompt in auth response
                pass
            
            # DO NOT store response in buffer - it contains handshake artifacts
            # Clear buffer after successful handshake
            self._buffer.clear()
        
        except Exception as e:
            self.close()
            raise ConnectionError(f"WebREPL handshake failed: {e}") from e
    
    def write(self, data: bytes) -> int:
        """
        Write data to WebREPL.
        
        Sends as text WebSocket frame (like web browser REPL does).
        MicroPython WebREPL expects text frames for REPL commands.
        
        :param data: Bytes to send (typically UTF-8 encoded text with line endings)
        :return: Number of bytes sent
        """
        if not self._ws:
            raise ConnectionError("WebREPL not connected")
        
        # Send as text frame (standard for WebREPL protocol)
        try:
            # Decode bytes to string for text frame
            if isinstance(data, bytes):
                text = data.decode('utf-8', errors='replace')
            else:
                text = data
            self._ws.send(text)
            return len(data) if isinstance(data, bytes) else len(text.encode('utf-8'))
        except Exception as e:
            raise TransportError(f"WebREPL write error: {e}") from e
    
    def read(self, size: int = 1) -> bytes:
        """Read data from WebREPL."""
        if not self._ws:
            raise ConnectionError("WebREPL not connected")
        
        # Fill buffer if needed
        while len(self._buffer) < size:
            try:
                data = self._ws.recv()
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self._buffer.extend(data)
            except self._ws_timeout_exc:
                break
            except Exception as e:
                raise TransportError(f"WebREPL read error: {e}") from e
        
        # Extract requested size
        result = bytes(self._buffer[:size])
        self._buffer = self._buffer[size:]
        return result
    
    def read_all(self) -> bytes:
        """Read all available data from WebREPL."""
        if not self._ws:
            raise ConnectionError("WebREPL not connected")
        
        # Try to read available data with short timeout
        try:
            self._ws.settimeout(0.01)
            while True:
                data = self._ws.recv()
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self._buffer.extend(data)
        except self._ws_timeout_exc:
            pass
        except Exception as e:
            raise TransportError(f"WebREPL read_all error: {e}") from e
        finally:
            self._ws.settimeout(self.timeout)
        
        result = bytes(self._buffer)
        self._buffer.clear()
        return result
    
    def in_waiting(self) -> int:
        """Return number of bytes in buffer."""
        # Try to peek at available data without blocking
        try:
            original_timeout = self._ws.gettimeout()
            self._ws.settimeout(0.001)
            data = self._ws.recv()
            if data:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self._buffer.extend(data)
            self._ws.settimeout(original_timeout)
        except self._ws_timeout_exc:
            self._ws.settimeout(original_timeout)
        except Exception as e:
            self._ws.settimeout(original_timeout)
            raise TransportError(f"WebREPL in_waiting error: {e}") from e
        
        return len(self._buffer)
    
    def read_available(self, timeout_ms: int = 10) -> bytes:
        """
        Non-blocking read from WebREPL.
        Returns immediately with available data or empty bytes after timeout.
        
        :param timeout_ms: Timeout in milliseconds
        :return: Available bytes or empty if no data
        """
        if not self._ws:
            raise ConnectionError("WebREPL not connected")
        
        try:
            original_timeout = self._ws.gettimeout()
            self._ws.settimeout(timeout_ms / 1000.0)
            
            # Try to receive data
            try:
                data = self._ws.recv()
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self._buffer.extend(data)
            except self._ws_timeout_exc:
                pass  # No data within window
            except Exception as e:
                raise TransportError(f"WebREPL read_available error: {e}") from e
            finally:
                self._ws.settimeout(original_timeout)
            
            # Return available data from buffer
            if self._buffer:
                result = bytes(self._buffer)
                self._buffer.clear()
                return result
            return b""
        
        except Exception as e:
            if isinstance(e, self._ws_timeout_exc):
                return b""
            raise TransportError(f"WebREPL read_available failure: {e}") from e
    
    def close(self) -> None:
        """Close WebREPL connection."""
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None
    
    def reset_input_buffer(self) -> None:
        """Clear input buffer."""
        self._buffer.clear()
        # Drain WebSocket
        try:
            self._ws.settimeout(0.01)
            while True:
                self._ws.recv()
        except self._ws_timeout_exc:
            pass
        except Exception as e:
            raise TransportError(f"WebREPL reset_input_buffer error: {e}") from e
        finally:
            self._ws.settimeout(self.timeout)
    
    def reset_output_buffer(self) -> None:
        """Clear output buffer (no-op for WebSocket)."""
        pass
    
    @property
    def is_open(self) -> bool:
        """Check if WebREPL is connected."""
        return self._ws is not None and self._ws.connected
    
    def put_file(self, source: str, dest: str, progress_callback=None) -> None:
        """
        Upload file using WebREPL binary protocol.
        
        :param source: Local file path
        :param dest: Remote file path on device
        :param progress_callback: Optional callback(bytes_sent, total_bytes)
        """
        import struct
        
        # Read file content
        with open(source, 'rb') as f:
            content = f.read()
        
        # WebREPL PUT command format:
        # "WA" (2 bytes) + file_size (4 bytes LE) + dest_path + \x00
        header = b"WA"
        header += struct.pack("<I", len(content))
        header += dest.encode('utf-8') + b"\x00"
        
        # Send header
        self._ws.send(header, opcode=self._websocket.ABNF.OPCODE_BINARY)
        
        # Wait for acknowledgment
        ack = self._ws.recv()
        if ack != b"\x00":
            raise IOError(f"WebREPL PUT failed: unexpected response {ack!r}")
        
        # Send file content in chunks
        chunk_size = 1024
        sent = 0
        while sent < len(content):
            chunk = content[sent:sent + chunk_size]
            self._ws.send(chunk, opcode=self._websocket.ABNF.OPCODE_BINARY)
            sent += len(chunk)
            
            if progress_callback:
                progress_callback(sent, len(content))
        
        # Wait for final acknowledgment
        final_ack = self._ws.recv()
        if final_ack != b"\x00":
            raise IOError(f"WebREPL PUT completion failed: {final_ack!r}")
    
    def get_file(self, source: str, dest: str, progress_callback=None) -> None:
        """
        Download file using WebREPL binary protocol.
        
        :param source: Remote file path on device
        :param dest: Local file path
        :param progress_callback: Optional callback(bytes_received, total_bytes)
        """
        import struct
        
        # WebREPL GET command format:
        # "WG" (2 bytes) + dummy_size (4 bytes) + source_path + \x00
        header = b"WG"
        header += struct.pack("<I", 0)  # Size is ignored for GET
        header += source.encode('utf-8') + b"\x00"
        
        # Send header
        self._ws.send(header, opcode=self._websocket.ABNF.OPCODE_BINARY)
        
        # Read file size response (4 bytes LE)
        size_data = self._ws.recv()
        if len(size_data) < 4:
            raise IOError(f"WebREPL GET failed: invalid size response")
        
        file_size = struct.unpack("<I", size_data[:4])[0]
        
        # Send acknowledgment
        self._ws.send(b"\x00", opcode=self._websocket.ABNF.OPCODE_BINARY)
        
        # Receive file content
        received = 0
        with open(dest, 'wb') as f:
            while received < file_size:
                chunk = self._ws.recv()
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                
                f.write(chunk)
                received += len(chunk)
                
                if progress_callback:
                    progress_callback(received, file_size)
        
        # Send final acknowledgment
        self._ws.send(b"\x00", opcode=self._websocket.ABNF.OPCODE_BINARY)
