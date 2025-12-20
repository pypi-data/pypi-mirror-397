"""IPC Protocol for replx agent communication (JSON over UDP)."""

import json
import struct
import time
import base64
from typing import Dict, Any, Optional, List


class AgentProtocol:
    """Handles message serialization/deserialization for agent IPC."""
    
    # Protocol constants
    MAX_UDP_SIZE = 65507  # Max UDP packet size
    MAX_PAYLOAD_SIZE = 60000  # Leave room for headers
    MAGIC = b'RPLX'  # Magic bytes for packet validation
    VERSION = 1
    
    @staticmethod
    def encode_message(msg: Dict[str, Any]) -> bytes:
        """
        Encode message as UDP packet.
        Format: [MAGIC:4][VERSION:1][LENGTH:4][JSON payload]
        """
        payload = json.dumps(msg).encode('utf-8')
        
        if len(payload) > AgentProtocol.MAX_PAYLOAD_SIZE:
            raise ValueError(f"Message too large: {len(payload)} bytes")
        
        header = (
            AgentProtocol.MAGIC +
            struct.pack('!B', AgentProtocol.VERSION) +
            struct.pack('!I', len(payload))
        )
        
        return header + payload
    
    @staticmethod
    def decode_message(data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decode UDP packet message.
        Returns None if invalid.
        """
        if len(data) < 9:  # Magic(4) + Version(1) + Length(4)
            return None
        
        # Validate magic
        if data[:4] != AgentProtocol.MAGIC:
            return None
        
        # Check version
        version = struct.unpack('!B', data[4:5])[0]
        if version != AgentProtocol.VERSION:
            return None
        
        # Extract length
        length = struct.unpack('!I', data[5:9])[0]
        
        if len(data) < 9 + length:
            return None
        
        # Parse JSON
        payload = data[9:9+length]
        return json.loads(payload.decode('utf-8'))
    
    @staticmethod
    def create_request(command: str, seq: int = None, **args) -> Dict[str, Any]:
        """Create a request message."""
        if seq is None:
            seq = int(time.time() * 1000000) % 0xFFFFFFFF  # Microsecond timestamp
        
        return {
            "seq": seq,
            "type": "request",
            "command": command,
            "args": args
        }
    
    @staticmethod
    def create_response(seq: int, result: Any = None, error: str = None) -> Dict[str, Any]:
        """Create a response message."""
        return {
            "seq": seq,
            "type": "response",
            "result": result,
            "error": error
        }
    
    @staticmethod
    def create_ack(seq: int) -> Dict[str, Any]:
        """Create an acknowledgment message."""
        return {
            "seq": seq,
            "type": "ack"
        }
    
    @staticmethod
    def create_stream(seq: int, data: bytes, stream_type: str = "stdout") -> Dict[str, Any]:
        """
        Create a stream message for real-time output.
        
        :param seq: Original request sequence number
        :param data: Output data as bytes
        :param stream_type: "stdout" or "stderr"
        """
        return {
            "seq": seq,
            "type": "stream",
            "data": base64.b64encode(data).decode('ascii'),
            "stream_type": stream_type
        }
    
    @staticmethod
    def create_progress_stream(seq: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a stream message for progress updates.
        
        :param seq: Original request sequence number
        :param progress_data: Progress information dict (current, total, file, etc.)
        """
        return {
            "seq": seq,
            "type": "stream",
            "data": progress_data,
            "stream_type": "progress"
        }
    
    @staticmethod
    def create_input(seq: int, data: bytes) -> Dict[str, Any]:
        """
        Create an input message for keyboard input to device.
        
        :param seq: Original request sequence number
        :param data: Input data as bytes
        """
        return {
            "seq": seq,
            "type": "input",
            "data": base64.b64encode(data).decode('ascii')
        }
    
    @staticmethod
    def decode_stream_data(msg: Dict[str, Any]) -> bytes:
        """Decode data from stream or input message."""
        data_b64 = msg.get('data', '')
        return base64.b64decode(data_b64) if data_b64 else b''
    
    @staticmethod
    def chunk_large_data(data: str, max_size: int = MAX_PAYLOAD_SIZE) -> List[str]:
        """
        Split large data into chunks.
        Used for responses with large output (e.g., ls -R).
        """
        chunks = []
        data_bytes = data.encode('utf-8')
        
        # Reserve space for JSON overhead (~100 bytes)
        chunk_size = max_size - 100
        
        for i in range(0, len(data_bytes), chunk_size):
            chunk = data_bytes[i:i+chunk_size].decode('utf-8', errors='ignore')
            chunks.append(chunk)
        
        return chunks
