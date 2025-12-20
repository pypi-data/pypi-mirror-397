"""
Agent server - maintains persistent connection to MicroPython device.

The agent runs as a background process and handles:
- Connection management (connect/disconnect)
- Command execution (exec, ls, cat, etc.)
- RAW REPL session persistence

Communication: UDP socket on port 49152 (localhost only)
"""

import gc
import os
import sys
import json
import socket
import threading
import time
import tempfile
from typing import Optional, Dict, Any

from ..protocol import ReplProtocol, create_storage
from ..exceptions import ProtocolError, TransportError
from .protocol import AgentProtocol

# Disable automatic GC - we'll control it manually to prevent random pauses
gc.disable()


class AgentServer:
    """Background agent server for persistent MicroPython connections."""
    
    DEFAULT_AGENT_PORT = 49152  # IANA Dynamic/Private range
    AGENT_HOST = '127.0.0.1'  # Localhost only for security
    
    def __init__(self, port: int = None):
        """Initialize agent server."""
        self.agent_port = port or self.DEFAULT_AGENT_PORT
        self.server_socket: Optional[socket.socket] = None
        self.running = False  # Agent running = Board connected
        self.repl_protocol: Optional[ReplProtocol] = None
        self.file_system = None  # DeviceStorage (serial or webrepl)
        
        # Connection info (valid when running=True)
        self.connection_type = ""
        self.port = ""
        self.core = ""
        self.device = ""
        self.manufacturer = "?"
        self.version = "?"  # version string (e.g., "1.27.0")
        self.device_root_fs = "/"
        
        # PID file for status checking
        self.pid_file = self._get_pid_file_path()
        
        # Interactive streaming state
        self._interactive_session: Optional[Dict[str, Any]] = None
        self._interactive_lock = threading.Lock()
        
        # Sequence tracking for duplicate detection
        self.last_seq = {}  # client_addr -> last_seq_number
        
        # REPL busy state - MicroPython REPL is single-threaded
        self._repl_busy = False
        self._repl_busy_lock = threading.Lock()
        self._repl_busy_client: Optional[tuple] = None  # (addr, command)
        
        # Connection health monitoring (for heartbeat + command tracking)
        self._command_in_progress = False
        self._last_command_time = time.time()
        self._command_lock = threading.Lock()
        self._heartbeat_thread: Optional[threading.Thread] = None
        
        # REPL session state
        self._repl_session_active = False
        self._repl_reader_thread: Optional[threading.Thread] = None
        self._repl_output_buffer = b""
        self._repl_buffer_lock = threading.Lock()
        
        # Run session state
        self._run_session_active = False
        self._run_buffer_lock = threading.Lock()
        self._run_completed = False
        self._run_error: Optional[str] = None
        self._run_detached = False  # Detached run in progress (drain thread active)
        self._drain_thread: Optional[threading.Thread] = None  # Drain thread for detach mode
    
    def _to_real_path(self, virtual_path: str) -> str:
        """
        Convert user-facing virtual path to actual filesystem path.
        E.g., /lib -> /flash/lib when device_root_fs is /flash
        """
        if self.device_root_fs == '/':
            return virtual_path
        
        # Ensure virtual path starts with /
        if not virtual_path.startswith('/'):
            virtual_path = '/' + virtual_path
        
        # device_root_fs has trailing slash, virtual_path starts with /
        # /flash/ + lib = /flash/lib
        if virtual_path == '/':
            return self.device_root_fs.rstrip('/')
        else:
            return self.device_root_fs.rstrip('/') + virtual_path
    
    def _to_virtual_path(self, real_path: str) -> str:
        """
        Convert actual filesystem path to user-facing virtual path.
        E.g., /flash/lib -> /lib when device_root_fs is /flash
        """
        if self.device_root_fs == '/':
            return real_path
        
        root = self.device_root_fs.rstrip('/')
        if real_path == root:
            return '/'
        elif real_path.startswith(root + '/'):
            return real_path[len(root):]
        else:
            # Path doesn't start with root - return as-is (shouldn't happen)
            return real_path
    
    def _get_pid_file_path(self) -> str:
        """Get PID file path (port-specific for multi-device support)."""
        return os.path.join(tempfile.gettempdir(), f'replx_agent_{self.agent_port}.pid')
    
    def start(self):
        """Start the agent server."""
        # Check if already running
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            # Check if process is alive
            try:
                if sys.platform == 'win32':
                    # Windows: check process existence
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    PROCESS_QUERY_INFORMATION = 0x0400
                    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, old_pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        raise RuntimeError(f"Agent already running (PID {old_pid})")
                else:
                    os.kill(old_pid, 0)  # Signal 0 checks existence
                    raise RuntimeError(f"Agent already running (PID {old_pid})")
            except (OSError, ProcessLookupError):
                # Process dead, remove stale PID file
                os.remove(self.pid_file)
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Create UDP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.AGENT_HOST, self.agent_port))
        
        self.running = True
        print(f"replx agent started (PID {os.getpid()})")
        print(f"Listening on {self.AGENT_HOST}:{self.agent_port} (UDP)")
        
        # Start heartbeat thread
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        
        try:
            self._serve()
        finally:
            self.cleanup()
    
    def _serve(self):
        """Main server loop."""
        while self.running:
            try:
                # Receive UDP packet
                data, client_addr = self.server_socket.recvfrom(AgentProtocol.MAX_UDP_SIZE)
                
                # Handle in a new thread for concurrency
                thread = threading.Thread(
                    target=self._handle_request,
                    args=(data, client_addr),
                    daemon=True
                )
                thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}", file=sys.stderr)
    
    def _heartbeat_loop(self):
        """Connection health monitoring - sends heartbeat if idle for 5+ seconds."""
        gc_counter = 0
        while self.running:
            time.sleep(1)  # Check every 1 second
            gc_counter += 1
            
            if not self.repl_protocol:
                continue  # No connection, skip
            
            # Skip heartbeat if interactive/detached run session is active
            # These sessions use the REPL and heartbeat would interrupt them
            # Check _run_detached FIRST and exit early
            with self._run_buffer_lock:
                detached = self._run_detached
                session_active = self._run_session_active
            
            if detached:
                continue
            if session_active:
                # Run GC during idle moments of active session (every 30 seconds)
                if gc_counter >= 30:
                    gc.collect()
                    gc_counter = 0
                continue
            
            with self._interactive_lock:
                if self._interactive_session:
                    continue
            
            # Check if command is in progress or recent (within 5 seconds)
            with self._command_lock:
                elapsed = time.time() - self._last_command_time
                if self._command_in_progress or elapsed < 5:
                    continue  # Skip heartbeat if busy or recent activity
            
            # Double-check _run_detached before sending heartbeat
            # (state may have changed during lock release)
            with self._run_buffer_lock:
                if self._run_detached:
                    continue
            
            # 5+ seconds idle: send heartbeat and run GC
            try:
                self.repl_protocol.exec("pass")
                with self._command_lock:
                    self._last_command_time = time.time()
                # Run GC when idle
                gc.collect()
                gc_counter = 0
            except Exception as e:
                # Connection lost - Agent must shutdown (running=connected)
                self.running = False  # This will exit the main loop
    
    def _start_drain_thread(self):
        """Start drain thread to consume serial data in detach mode."""
        def drain_loop():
            while self._run_detached and self.running:
                try:
                    if self.repl_protocol and self.repl_protocol.transport:
                        self.repl_protocol.transport.read_available()
                except Exception:
                    pass
                time.sleep(0.05)
        
        self._stop_drain_thread()
        
        self._drain_thread = threading.Thread(target=drain_loop, daemon=True)
        self._drain_thread.start()
    
    def _stop_drain_thread(self):
        """Stop the drain thread."""
        if self._drain_thread and self._drain_thread.is_alive():
            self._drain_thread.join(timeout=1.0)
        self._drain_thread = None
    
    def _stop_detached_script(self):
        """Stop a detached script if running."""
        if not self._run_detached:
            return
        
        with self._run_buffer_lock:
            self._run_detached = False
        
        self._stop_drain_thread()
        
        if self.repl_protocol and self.repl_protocol.transport:
            try:
                self.repl_protocol.transport.write(b'\x03')
                time.sleep(0.05)
                self.repl_protocol.transport.write(b'\x03')
                time.sleep(0.1)
                self.repl_protocol.transport.read_available()
            except Exception:
                pass
    
    def _handle_request(self, data: bytes, client_addr: tuple):
        """Handle a single UDP request."""
        try:
            # Decode message
            msg = AgentProtocol.decode_message(data)
            if not msg:
                print(f"Invalid message from {client_addr}", file=sys.stderr)
                return
            
            seq = msg.get('seq', 0)
            msg_type = msg.get('type', 'request')
            
            # Handle input messages for interactive session (no response needed)
            if msg_type == 'input':
                self._handle_input(msg, client_addr)
                return
            
            # Check for duplicate (idempotency) - only for requests
            if msg_type == 'request':
                if client_addr in self.last_seq and seq <= self.last_seq[client_addr]:
                    # Duplicate request, ignore (client will retry if needed)
                    return
                
                self.last_seq[client_addr] = seq
            
            # Send immediate ACK (fast path)
            ack = AgentProtocol.create_ack(seq)
            ack_data = AgentProtocol.encode_message(ack)
            self.server_socket.sendto(ack_data, client_addr)
            
            # Fast path: Check REPL busy state before processing command
            # This allows quick rejection without blocking streaming output
            command = msg.get('command')
            NON_REPL_COMMANDS = {'connect', 'free', 'status', 'shutdown', 'ping', 'run_stop'}
            
            if command not in NON_REPL_COMMANDS:
                # Quick non-blocking check for busy state
                if self._repl_busy:
                    response = AgentProtocol.create_response(
                        seq=seq,
                        error="Device is busy. Another command is currently running. Please wait for it to complete or press Ctrl+C to cancel."
                    )
                    response_data = AgentProtocol.encode_message(response)
                    self.server_socket.sendto(response_data, client_addr)
                    return
            
            # Process command
            response = self._handle_message(msg, client_addr)
            
            # Send response (None means streaming - response will be sent later)
            if response is not None:
                response_data = AgentProtocol.encode_message(response)
                self.server_socket.sendto(response_data, client_addr)
            
        except Exception as e:
            # Send error response
            try:
                error_response = AgentProtocol.create_response(
                    seq=msg.get('seq', 0) if msg else 0,
                    error=str(e)
                )
                error_data = AgentProtocol.encode_message(error_response)
                self.server_socket.sendto(error_data, client_addr)
            except Exception:
                pass
    
    def _handle_message(self, msg: dict, client_addr: tuple = None) -> dict:
        """Handle a request message and return response."""
        command = msg.get('command')
        args = msg.get('args', {})
        seq = msg.get('seq', 0)
        
        # Commands that don't use REPL (always allowed)
        NON_REPL_COMMANDS = {'connect', 'free', 'status', 'shutdown', 'ping', 'run_stop'}
        
        # If a detached script is running and this command uses REPL,
        # stop the detached script first (Ctrl+C + drain thread cleanup)
        if command not in NON_REPL_COMMANDS and self._run_detached:
            self._stop_detached_script()
        
        # Mark command as in progress (for heartbeat coordination)
        with self._command_lock:
            self._command_in_progress = True
        
        # Mark REPL as busy for commands that use it
        # Note: Fast-path busy check is already done in _handle_request
        if command not in NON_REPL_COMMANDS:
            # Set busy flag (atomic operation, minimal lock time)
            with self._repl_busy_lock:
                # Double-check in case of race condition
                if self._repl_busy:
                    with self._command_lock:
                        self._command_in_progress = False
                    return AgentProtocol.create_response(
                        seq=seq,
                        error="Device is busy. Another command is currently running. Please wait for it to complete or press Ctrl+C to cancel."
                    )
                self._repl_busy = True
                self._repl_busy_client = (client_addr, command)
        
        try:
            if command == 'connect':
                result = self._cmd_connect(**args)
            elif command == 'free':
                result = self._cmd_free()
            elif command == 'exec':
                result = self._cmd_exec(**args)
            elif command == 'status':
                result = self._cmd_status()
            elif command == 'shutdown':
                result = self._cmd_shutdown()
            elif command == 'ping':
                result = {"pong": True}
            elif command == 'reset':
                result = self._cmd_reset()
            elif command == 'run':
                result = self._cmd_run(**args)
            elif command == 'run_interactive':
                # Interactive run returns None - response is sent via streaming
                # Note: busy flag will be cleared in _run_interactive_thread completion
                self._cmd_run_interactive(seq, client_addr, **args)
                return None  # Response will be sent when execution completes
            elif command == 'run_stop':
                result = self._cmd_run_stop()
            elif command == 'ls':
                result = self._cmd_ls(**args)
            elif command == 'ls_recursive':
                result = self._cmd_ls_recursive(**args)
            elif command == 'cat':
                result = self._cmd_cat(**args)
            elif command == 'rm':
                result = self._cmd_rm(**args)
            elif command == 'rmdir':
                result = self._cmd_rmdir(**args)
            elif command == 'mkdir':
                result = self._cmd_mkdir(**args)
            elif command == 'is_dir':
                result = self._cmd_is_dir(**args)
            elif command == 'mem':
                result = self._cmd_mem()
            elif command == 'cp':
                result = self._cmd_cp(**args)
            elif command == 'mv':
                result = self._cmd_mv(**args)
            elif command == 'df':
                result = self._cmd_df()
            elif command == 'touch':
                result = self._cmd_touch(**args)
            elif command == 'format':
                result = self._cmd_format()
            elif command == 'get_file':
                result = self._cmd_get_file(**args)
            elif command == 'get_to_local':
                result = self._cmd_get_to_local(**args)
            elif command == 'getdir_to_local':
                # Streaming directory download - returns None, response sent via streaming
                self._cmd_getdir_to_local_streaming(seq, client_addr, **args)
                return None
            elif command == 'put_file':
                result = self._cmd_put_file(**args)
            elif command == 'put_from_local':
                result = self._cmd_put_from_local(**args)
            elif command == 'put_from_local_streaming':
                # Streaming upload - returns None, response sent via streaming
                self._cmd_put_from_local_streaming(seq, client_addr, **args)
                return None
            elif command == 'putdir_from_local':
                result = self._cmd_putdir_from_local(**args)
            elif command == 'putdir_from_local_streaming':
                # Streaming directory upload - returns None, response sent via streaming
                self._cmd_putdir_from_local_streaming(seq, client_addr, **args)
                return None
            elif command == 'put_file_batch':
                result = self._cmd_put_file_batch(**args)
            elif command == 'get_file_batch':
                result = self._cmd_get_file_batch(**args)
            elif command == 'stat':
                result = self._cmd_stat(**args)
            elif command == 'repl_enter':
                result = self._cmd_repl_enter()
            elif command == 'repl_exit':
                result = self._cmd_repl_exit()
            elif command == 'repl_write':
                result = self._cmd_repl_write(**args)
            elif command == 'repl_read':
                result = self._cmd_repl_read()
            else:
                raise ValueError(f"Unknown command: {command}")
            
            return AgentProtocol.create_response(seq=seq, result=result)
        
        except (TransportError, ConnectionError, OSError, BrokenPipeError) as e:
            # Connection lost - shutdown agent (running=connected)
            self.running = False
            return AgentProtocol.create_response(seq=seq, error=f"Connection lost: {str(e)}. Agent shutting down.")
        
        except Exception as e:
            return AgentProtocol.create_response(seq=seq, error=str(e))
        
        finally:
            # Release REPL busy flag (except for run_interactive which handles it separately)
            if command not in NON_REPL_COMMANDS and command != 'run_interactive':
                with self._repl_busy_lock:
                    self._repl_busy = False
                    self._repl_busy_client = None
            
            # Update command tracking
            with self._command_lock:
                self._command_in_progress = False
                self._last_command_time = time.time()
    
    def _cmd_connect(self, port: str = None, target: str = None, core: str = "RP2350", 
                     device: str = None, device_root_fs: str = "/") -> dict:
        """Handle connect command."""
        if self.repl_protocol is not None:
            raise RuntimeError("Already connected. Use 'replx free' first.")
        
        # Determine connection type
        if target:
            connection_type = "webrepl"
            if ':' not in target:
                raise ValueError("Invalid WebREPL target format (expected IP:PASSWORD)")
            ip_address, password = target.rsplit(':', 1)
            conn_port = f"ws://{ip_address}:8266"
            conn_password = password
        elif port:
            connection_type = "serial"
            conn_port = port
            conn_password = ""
        else:
            raise ValueError("Either port or target required")
        
        # Create ReplProtocol
        self.repl_protocol = ReplProtocol(
            port=conn_port,
            baudrate=115200,
            core=core,
            device_root_fs=device_root_fs,
            password=conn_password
        )
        
        # Detect device info
        try:
            import time
            
            # Use ReplProtocol's existing transport
            transport = self.repl_protocol.transport
            
            # WebREPL vs Serial handling
            if connection_type == "webrepl":
                # WebREPL is always in Friendly REPL mode (no Raw REPL)
                # For now, use simple defaults: device name and version from command args
                # Full device detection can be added later when WebREPL Raw REPL support is implemented
                
                detected_device = device if device else "ticle"  # Default to ticle if not specified
                detected_core = core  # Use the provided core (default RP2350)
                
                # Version: for now use 1.26.0 as default (known TiCLE firmware version)
                # This can be improved by parsing device info from WebREPL in friendly mode
                self.version = "1.26.0"
                
                self.core = detected_core
                self.device = detected_device
                self.manufacturer = "Hanback Electronics"  # Default for WebREPL (usually TiCLE)
                
            else:
                # Serial: Use Raw REPL mode to get banner
                transport.write(b'\r\x03')  # Ctrl-C: interrupt current execution
                time.sleep(0.1)
                transport.reset_input_buffer()  # Clear any pending data
                
                transport.write(b'\r\x02')  # Ctrl-B: exit raw REPL, show banner
                time.sleep(0.2)  # Give device time to respond
                
                res = transport.read_available()  # Read the banner response
                
                if res:
                    res_str = res.decode('utf-8', errors='replace') if isinstance(res, bytes) else res
                    
                    # Use common parsing function
                    from ..cli.helpers import parse_device_banner
                    result = parse_device_banner(res_str)
                    
                    if result:
                        # parse_device_banner returns (version, core, device, manufacturer)
                        version, detected_core, detected_device, manufacturer = result
                        self.version = version
                        self.device = detected_device
                        self.core = detected_core
                        self.manufacturer = manufacturer
                    else:
                        # Fallback: try simple version extraction using friendly REPL
                        transport.write(b'import sys; print(sys.version.split()[0])\r\n')
                        time.sleep(0.2)
                        ver_res = transport.read_available()
                        if ver_res:
                            ver_str = ver_res.decode('utf-8', errors='replace') if isinstance(ver_res, bytes) else ver_res
                            # Extract version like "1.27.0" from response
                            import re
                            match = re.search(r'(\d+\.\d+(?:\.\d+)?)', ver_str)
                            if match:
                                self.version = match.group(1)
                        self.device = core  # fallback to core name
        except Exception as e:
            self.repl_protocol.close()
            self.repl_protocol = None
            raise RuntimeError(f"Failed to detect device: {e}")
        
        # Set state (running is already True from start())
        self.connection_type = connection_type
        self.port = conn_port
        # self.device and self.core already set by detection above
        
        # Set device_root_fs based on core type
        from replx.cli.helpers import get_root_fs_for_core
        self.device_root_fs = get_root_fs_for_core(self.core)
        # Ensure trailing slash for consistency
        if not self.device_root_fs.endswith('/'):
            self.device_root_fs += '/'
        
        self.file_system = create_storage(
            self.repl_protocol,
            core=self.core,
            device=self.device,
            device_root_fs=self.device_root_fs,
        )
        
        return {
            "connected": True,
            "connection_type": connection_type,
            "device": self.device,
            "core": self.core,
            "version": self.version
        }
    
    def _cmd_free(self) -> dict:
        """Handle free command - release port and shutdown agent.
        
        Since running=connected, freeing the port means shutting down the agent.
        The client can restart the agent with the next command if needed.
        """
        port = self.port  # Save for response
        
        if self.repl_protocol:
            try:
                self.repl_protocol._leave_repl()
            except Exception:
                pass
            self.repl_protocol.close()
            self.repl_protocol = None
        
        self.file_system = None
        self.running = False  # This will stop the agent
        
        return {"released": True, "port": port}
    
    def _cmd_exec(self, code: str, interactive: bool = False) -> dict:
        """Handle exec command."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        result = self.repl_protocol.exec(code)
        result_str = result.decode('utf-8', errors='replace') if isinstance(result, bytes) else result
        
        # Check if result is too large for single UDP packet
        if len(result_str) > AgentProtocol.MAX_PAYLOAD_SIZE - 1000:
            # Truncate with warning
            result_str = result_str[:AgentProtocol.MAX_PAYLOAD_SIZE - 1100] + "\n... [output truncated]"
        
        return {"output": result_str}
    
    def _cmd_status(self) -> dict:
        """Handle status command."""
        with self._repl_busy_lock:
            busy = self._repl_busy
            busy_command = self._repl_busy_client[1] if self._repl_busy_client else None
        
        return {
            "running": True,
            "connected": self.repl_protocol is not None,
            "connection_type": self.connection_type,
            "port": self.port,
            "device": self.device,
            "core": self.core,
            "manufacturer": self.manufacturer,
            "version": self.version,
            "in_raw_repl": self.repl_protocol._in_raw_repl if self.repl_protocol else False,
            "pid": os.getpid(),
            "busy": busy,
            "busy_command": busy_command
        }
    
    def _cmd_shutdown(self) -> dict:
        """Handle shutdown command."""
        self.running = False
        if self.repl_protocol:
            try:
                self._cmd_free()
            except Exception:
                pass
        return {"shutdown": True}
    
    def _cmd_reset(self) -> dict:
        """Handle reset command."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        self.repl_protocol.reset()
        return {"reset": True}
    
    def _handle_input(self, msg: dict, client_addr: tuple):
        """Handle input message from client during interactive session."""
        with self._interactive_lock:
            if not self._interactive_session:
                return  # No active session
            
            if self._interactive_session.get('client_addr') != client_addr:
                return  # Not from the session owner
            
            # Decode input data
            input_data = AgentProtocol.decode_stream_data(msg)
            if input_data:
                # Add to input queue for the execution thread
                input_queue = self._interactive_session.get('input_queue')
                if input_queue is not None:
                    input_queue.append(input_data)
    
    def _cmd_run_interactive(self, seq: int, client_addr: tuple, script_path: str = None, 
                              script_content: str = None, echo: bool = False):
        """
        Handle interactive run command with streaming output.
        
        Runs script in a separate thread and streams output to client.
        """
        if not self.repl_protocol:
            # Send error response
            error_response = AgentProtocol.create_response(seq=seq, error="Not connected")
            error_data = AgentProtocol.encode_message(error_response)
            self.server_socket.sendto(error_data, client_addr)
            return
        
        # Check if interactive session already active
        with self._interactive_lock:
            if self._interactive_session:
                error_response = AgentProtocol.create_response(
                    seq=seq, error="Interactive session already active"
                )
                error_data = AgentProtocol.encode_message(error_response)
                self.server_socket.sendto(error_data, client_addr)
                return
        
        # Get script content
        if script_path:
            import os as os_module
            if not os_module.path.exists(script_path):
                error_response = AgentProtocol.create_response(
                    seq=seq, error=f"Script not found: {script_path}"
                )
                error_data = AgentProtocol.encode_message(error_response)
                self.server_socket.sendto(error_data, client_addr)
                return
            
            with open(script_path, 'rb') as f:
                script_data = f.read()
        elif script_content:
            script_data = script_content.encode('utf-8') if isinstance(script_content, str) else script_content
        else:
            error_response = AgentProtocol.create_response(
                seq=seq, error="Either script_path or script_content required"
            )
            error_data = AgentProtocol.encode_message(error_response)
            self.server_socket.sendto(error_data, client_addr)
            return
        
        # Create session
        session = {
            'seq': seq,
            'client_addr': client_addr,
            'echo': echo,
            'input_queue': [],
            'stop_requested': False,
            'thread': None
        }
        
        with self._interactive_lock:
            self._interactive_session = session
        
        # Initialize run session state BEFORE starting thread
        with self._run_buffer_lock:
            self._run_session_active = True
            self._run_completed = False
            self._run_error = None
        
        # Start execution thread
        thread = threading.Thread(
            target=self._run_interactive_thread,
            args=(session, script_data),
            daemon=True
        )
        session['thread'] = thread
        thread.start()
        
        # Return None - ACK already sent by _handle_request, client starts polling
    
    def _run_interactive_thread(self, session: dict, script_data: bytes):
        """Execute script and push output directly to client via UDP.
        
        Push-based streaming: Server sends output directly to client as it arrives,
        eliminating polling latency and preventing buffer buildup.
        """
        # Capture socket and client info for direct UDP push
        sock = self.server_socket
        client_addr = session['client_addr']
        seq = session['seq']
        
        # Buffer for batching small chunks (reduces UDP packet overhead)
        output_buffer = bytearray()
        buffer_lock = threading.Lock()  # Protect buffer access from flush timer
        BUFFER_FLUSH_SIZE = 4096  # Flush when buffer reaches this size
        last_flush_time = [time.time()]
        FLUSH_INTERVAL = 0.05  # Flush at least every 50ms for responsiveness
        
        def flush_buffer():
            """Send buffered output to client via UDP."""
            nonlocal output_buffer
            with buffer_lock:
                if not output_buffer:
                    return
                data_to_send = bytes(output_buffer)
                output_buffer.clear()
                last_flush_time[0] = time.time()
            
            try:
                stream_msg = {
                    'type': 'stream',
                    'seq': seq,
                    'output': data_to_send.decode('utf-8', errors='replace')
                }
                stream_data = AgentProtocol.encode_message(stream_msg)
                sock.sendto(stream_data, client_addr)
            except Exception:
                pass  # Best effort - don't crash on send failure
        
        def data_consumer(chunk: bytes):
            """Callback for _exec() - buffer and push output to client."""
            nonlocal output_buffer
            if not chunk:
                return
            # Filter control characters
            filtered = chunk.replace(b'\x04', b'').replace(b'\r', b'')
            if not filtered:
                return
            
            # Add to buffer
            with buffer_lock:
                output_buffer.extend(filtered)
                buffer_size = len(output_buffer)
                time_elapsed = time.time() - last_flush_time[0]
            
            # Flush if buffer is large enough or time elapsed
            if buffer_size >= BUFFER_FLUSH_SIZE or time_elapsed >= FLUSH_INTERVAL:
                flush_buffer()
        
        # Periodic flush timer thread - ensures prompts from input() are sent
        flush_timer_running = [True]
        
        def flush_timer():
            while flush_timer_running[0]:
                time.sleep(FLUSH_INTERVAL)
                flush_buffer()
        
        flush_thread = threading.Thread(target=flush_timer, daemon=True)
        flush_thread.start()
        
        try:
            repl = self.repl_protocol
            
            # Input handling thread
            input_thread_running = [True]
            
            def input_handler():
                while input_thread_running[0] and not session.get('stop_requested'):
                    input_data = None
                    with self._interactive_lock:
                        if session.get('input_queue'):
                            input_data = session['input_queue'].pop(0)
                    
                    if input_data:
                        try:
                            if input_data == b'\x03':  # Ctrl+C
                                repl.transport.write(b'\x03')
                                repl._interrupt_requested = True
                            elif input_data == b'\x04':  # Ctrl+D
                                repl.transport.write(b'\x04')
                            elif input_data in (b'\n', b'\r'):
                                repl.transport.write(b'\r')
                            else:
                                repl.transport.write(input_data)
                        except:
                            pass
                    time.sleep(0.01)
            
            input_thread = threading.Thread(target=input_handler, daemon=True)
            input_thread.start()
            
            try:
                # Ensure raw REPL mode
                if not repl._in_raw_repl:
                    repl._enter_repl()
                
                # Execute using _exec() with data_consumer
                repl._exec(script_data, interactive=False, echo=False, detach=False, 
                          data_consumer=data_consumer)
                
            except ProtocolError as e:
                with self._run_buffer_lock:
                    self._run_error = str(e)
                
            finally:
                input_thread_running[0] = False
                flush_timer_running[0] = False  # Stop flush timer
                # Flush any remaining buffered output
                flush_buffer()
            
            # Mark completion and send completion message to client
            with self._run_buffer_lock:
                self._run_completed = True
            
            # Send completion message to client
            try:
                complete_msg = {
                    'type': 'stream',
                    'seq': seq,
                    'output': '',
                    'completed': True,
                    'error': None
                }
                complete_data = AgentProtocol.encode_message(complete_msg)
                sock.sendto(complete_data, client_addr)
            except Exception:
                pass
            
            # Clean up device state after script execution
            # Send Ctrl+C to interrupt any remaining state, then re-enter raw REPL
            try:
                repl.transport.write(b'\x03')  # Ctrl+C
                time.sleep(0.05)
                repl.transport.write(b'\x03')  # Ctrl+C again
                time.sleep(0.1)
                # Try to re-enter raw REPL for next command
                repl._enter_repl()
            except Exception:
                pass  # Best effort cleanup
                
        except Exception as e:
            flush_timer_running[0] = False  # Stop flush timer on exception
            with self._run_buffer_lock:
                self._run_error = str(e)
                self._run_completed = True
            # Send error completion to client
            try:
                error_msg = {
                    'type': 'stream',
                    'seq': seq,
                    'output': '',
                    'completed': True,
                    'error': str(e)
                }
                error_data = AgentProtocol.encode_message(error_msg)
                sock.sendto(error_data, client_addr)
            except Exception:
                pass
            # Also clean up on exception
            try:
                if self.repl_protocol:
                    self.repl_protocol.transport.write(b'\x03')
                    time.sleep(0.05)
                    self.repl_protocol.transport.write(b'\x03')
                    time.sleep(0.1)
                    self.repl_protocol._enter_repl()
            except Exception:
                pass
        finally:
            flush_timer_running[0] = False  # Ensure flush timer stops
            with self._interactive_lock:
                self._interactive_session = None
            with self._repl_busy_lock:
                self._repl_busy = False
                self._repl_busy_client = None
            with self._command_lock:
                self._command_in_progress = False
                self._last_command_time = time.time()
    
    def _cmd_run_stop(self) -> dict:
        """Stop current interactive run session."""
        with self._interactive_lock:
            if not self._interactive_session:
                return {"stopped": False, "reason": "No active session"}
            
            self._interactive_session['stop_requested'] = True
            
            # Send interrupt to device multiple times to ensure it's received
            if self.repl_protocol:
                try:
                    self.repl_protocol.transport.write(b'\x03')  # Ctrl+C
                    time.sleep(0.05)
                    self.repl_protocol.transport.write(b'\x03')  # Ctrl+C again
                except Exception:
                    pass
        
        # Wait for session to clear (max 1 second)
        for _ in range(20):
            time.sleep(0.05)
            with self._interactive_lock:
                if not self._interactive_session:
                    return {"stopped": True}
        
        # Force clear if still active
        with self._interactive_lock:
            self._interactive_session = None
        
        return {"stopped": True}
    
    def _cmd_run(self, script_path: str = None, script_content: str = None, detach: bool = False) -> dict:
        """Handle run command - send script to device and optionally wait for output.
        
        Args:
            script_path: Path to the script file to execute
            script_content: Script content as string (alternative to script_path)
            detach: If True, send script and return immediately without waiting for output
                    The script runs in Friendly REPL mode (not raw REPL) so heartbeat
                    won't interfere. Use _run_detached flag to prevent heartbeat anyway.
        """
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        # Get script content
        if script_path:
            import os as os_module
            if not os_module.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Read script content
            with open(script_path, 'rb') as f:
                script_data = f.read()
            display_name = script_path
        elif script_content:
            script_data = script_content.encode('utf-8') if isinstance(script_content, str) else script_content
            display_name = "<inline>"
        else:
            raise RuntimeError("Either script_path or script_content required")
        
        if detach:
            # Non-interactive (detach) mode:
            # 1. Execute script in Friendly REPL paste mode (Ctrl+E)
            # 2. Start drain thread to consume serial output
            # 
            # The drain thread prevents serial buffer overflow:
            # - Board script may print() continuously, filling serial TX buffer
            # - If PC doesn't read, board blocks on print() -> script hangs
            # - Drain thread keeps buffer empty so script runs smoothly
            # 
            # When another command is executed, _stop_detached_script() is called
            # which stops drain thread, sends Ctrl+C, and clears state.
            try:
                # Mark detached run to prevent heartbeat interference
                with self._run_buffer_lock:
                    self._run_detached = True
                
                # Exit raw REPL if in it, enter Friendly REPL
                try:
                    self.repl_protocol._leave_repl()
                except Exception:
                    pass
                self.repl_protocol._in_raw_repl = False
                
                # Send Ctrl+C to interrupt any running code, then Ctrl+B for Friendly REPL
                self.repl_protocol.transport.write(b'\x03')  # Ctrl+C
                time.sleep(0.05)
                self.repl_protocol.transport.write(b'\x03')  # Ctrl+C again
                time.sleep(0.05)
                self.repl_protocol.transport.write(b'\x02')  # Ctrl+B (Friendly REPL)
                time.sleep(0.1)
                
                # Clear any pending data
                try:
                    self.repl_protocol.transport.read_available()
                except Exception:
                    pass
                
                # Use paste mode (Ctrl+E) for reliable multiline execution
                # Ctrl+E enters paste mode, then we send code, then Ctrl+D to execute
                self.repl_protocol.transport.write(b'\x05')  # Ctrl+E (paste mode)
                time.sleep(0.2)
                
                # Read paste mode prompt
                try:
                    self.repl_protocol.transport.read_available()
                except Exception:
                    pass
                
                # Send script content line by line
                script_str = script_data.decode('utf-8', errors='replace')
                lines = script_str.split('\n')
                for line in lines:
                    self.repl_protocol.transport.write(line.encode('utf-8') + b'\r')
                    time.sleep(0.01)  # Small delay between lines
                
                # Ctrl+D to finish paste mode and execute
                time.sleep(0.1)
                self.repl_protocol.transport.write(b'\x04')  # Ctrl+D
                
                # Brief wait and read initial response to confirm execution started
                time.sleep(0.3)
                try:
                    self.repl_protocol.transport.read_available()
                except Exception:
                    pass
                
                # Start drain thread to continuously consume serial output
                # This prevents buffer overflow which would block print() on board
                self._start_drain_thread()
                
                # Return immediately - script continues running with drain thread active
                # _run_detached=True, drain thread running
                # Next command will call _stop_detached_script() to clean up
                return {"run": True, "script": display_name, "detached": True}
            except Exception as e:
                with self._run_buffer_lock:
                    self._run_detached = False
                raise RuntimeError(f"Script send failed: {e}")
        else:
            # Wait for output (legacy behavior)
            try:
                if script_path:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        script_code = f.read()
                else:
                    script_code = script_content if isinstance(script_content, str) else script_content.decode('utf-8')
                output = self.repl_protocol.exec(script_code)
                
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='replace')
                
                return {"run": True, "script": display_name, "output": output}
            except Exception as e:
                raise RuntimeError(f"Script execution failed: {e}")
    
    def _cmd_ls(self, path: str = "/", detailed: bool = False, recursive: bool = False) -> dict:
        """Handle ls command.
        
        Converts virtual paths to real paths for filesystem operations,
        and converts real paths back to virtual paths for client display.
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            
            if detailed or recursive:
                items = self.file_system.ls_detailed(real_path)
                if recursive:
                    # Simple recursive implementation
                    all_items = []
                    def recurse(p):
                        try:
                            items = self.file_system.ls_detailed(p)
                            for name, size, is_dir in items:
                                full_path = f"{p.rstrip('/')}/{name}"
                                all_items.append((full_path, size, is_dir))
                                if is_dir:
                                    recurse(full_path)
                        except:
                            pass
                    recurse(real_path)
                    items = all_items
                
                # Convert real paths back to virtual paths for client
                return {
                    "items": [{"name": self._to_virtual_path(n), "size": s, "is_dir": d} for n, s, d in items]
                }
            else:
                items = self.file_system.ls(real_path)
                return {"items": items}
        except Exception as e:
            raise RuntimeError(f"ls failed: {e}")
    
    def _cmd_cat(self, path: str) -> dict:
        """Handle cat command - read file content from device (get with no local path)."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            
            # Use file_system.get() with no local path to get content as bytes
            content = self.file_system.get(real_path)
            
            # Check if binary (contains NULL bytes)
            is_binary = b'\x00' in content
            
            if is_binary:
                # Binary file - return as hex string with flag
                return {
                    "content": content.hex(),
                    "is_binary": True,
                    "size": len(content)
                }
            else:
                # Try to decode as text
                try:
                    text_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    # Not valid UTF-8 but no NULL bytes - treat as binary
                    return {
                        "content": content.hex(),
                        "is_binary": True,
                        "size": len(content)
                    }
                
                # Check size limit
                if len(text_content) > AgentProtocol.MAX_PAYLOAD_SIZE - 1000:
                    text_content = text_content[:AgentProtocol.MAX_PAYLOAD_SIZE - 1100] + "\n... [truncated]"
                
                return {"content": text_content, "is_binary": False}
        except Exception as e:
            raise RuntimeError(f"cat failed: {e}")
    
    def _cmd_rm(self, path: str, recursive: bool = False) -> dict:
        """Handle rm command."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            if recursive:
                self.file_system.rmdir(real_path)
            else:
                self.file_system.rm(real_path)
            return {"removed": path}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"rm failed: {e}")
    
    def _cmd_rmdir(self, path: str) -> dict:
        """Handle rmdir command - remove directory recursively."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            self.file_system.rmdir(real_path)
            return {"removed": path}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"rmdir failed: {e}")
    
    def _cmd_mkdir(self, path: str) -> dict:
        """Handle mkdir command."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            self.file_system.mkdir(real_path)
            return {"created": path}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"mkdir failed: {e}")
    
    def _cmd_is_dir(self, path: str) -> dict:
        """Handle is_dir command - check if path is a directory."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            result = self.file_system.is_dir(real_path)
            return {"path": path, "is_dir": result}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"is_dir failed: {e}")
    
    def _cmd_mem(self) -> dict:
        """Handle mem command - get memory information."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            result = self.file_system.mem()
            return {"mem": result}
        except Exception as e:
            raise RuntimeError(f"mem failed: {e}")
    
    def _cmd_df(self) -> dict:
        """Handle df command - get filesystem information."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            result = self.file_system.df()
            # result is (total, used, free, percent)
            return {
                "total": result[0],
                "used": result[1],
                "free": result[2],
                "percent": result[3]
            }
        except Exception as e:
            raise RuntimeError(f"df failed: {e}")
    
    def _cmd_touch(self, path: str) -> dict:
        """Handle touch command - create empty file."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            command = f"f = open('{real_path}', 'a'); f.close()"
            self.repl_protocol.exec(command)
            return {"created": path}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"touch failed: {e}")
    
    def _cmd_format(self) -> dict:
        """Handle format command - format filesystem."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            result = self.file_system.format()
            return {"formatted": result}
        except Exception as e:
            import traceback
            raise RuntimeError(f"format failed: {e}\n{traceback.format_exc()}")
    
    def _cmd_get_file(self, remote_path: str) -> dict:
        """Handle get_file command - returns file content."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(remote_path)
            content = self.file_system.get(real_path)
            # Check size limit
            if len(content) > AgentProtocol.MAX_PAYLOAD_SIZE - 1000:
                raise RuntimeError(f"File too large for UDP transfer: {len(content)} bytes")
            return {"content": content, "path": remote_path}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"get_file failed: {e}")
    
    def _cmd_put_file(self, remote_path: str, content: str) -> dict:
        """Handle put_file command - uploads file content."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(remote_path)
            
            # Write content to temporary file then upload
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as f:
                f.write(content)
                temp_path = f.name
            
            try:
                self.file_system.put(temp_path, real_path)
            finally:
                import os as os_module
                if os_module.path.exists(temp_path):
                    os_module.remove(temp_path)
            
            return {"uploaded": remote_path}  # Return virtual path to user
        except Exception as e:
            raise RuntimeError(f"put_file failed: {e}")
    
    def _cmd_put_file_batch(self, file_specs: list) -> dict:
        """Handle put_file_batch command - uploads multiple files efficiently.
        
        Args:
            file_specs: List of dicts with 'local_path', 'remote_path', and 'content' (base64)
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        import base64
        import tempfile
        import os as os_module
        
        results = []
        try:
            for spec in file_specs:
                local_path = spec.get('local_path')
                remote_path = spec.get('remote_path')
                content_b64 = spec.get('content')
                
                # Convert user path to real filesystem path
                real_path = self._to_real_path(remote_path)
                
                # If content is provided (base64), write to temp file
                if content_b64:
                    content_bytes = base64.b64decode(content_b64)
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.tmp') as f:
                        f.write(content_bytes)
                        local_path = f.name
                    
                    try:
                        self.file_system.put(local_path, real_path)
                        results.append({"path": remote_path, "success": True})  # Return virtual path
                    except Exception as e:
                        results.append({"path": remote_path, "success": False, "error": str(e)})
                    finally:
                        if os_module.path.exists(local_path):
                            os_module.remove(local_path)
                elif local_path and os_module.path.exists(local_path):
                    try:
                        self.file_system.put(local_path, real_path)
                        results.append({"path": remote_path, "success": True})  # Return virtual path
                    except Exception as e:
                        results.append({"path": remote_path, "success": False, "error": str(e)})
                else:
                    results.append({"path": remote_path, "success": False, "error": "No content or local_path"})
            
            success_count = sum(1 for r in results if r['success'])
            return {"results": results, "success_count": success_count, "total": len(file_specs)}
        except Exception as e:
            raise RuntimeError(f"put_file_batch failed: {e}")
    
    def _cmd_get_file_batch(self, remote_paths: list) -> dict:
        """Handle get_file_batch command - downloads multiple files efficiently.
        
        Args:
            remote_paths: List of remote file paths to download
        
        Returns:
            Dict with file contents (base64 encoded) for each path
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        import base64
        
        results = []
        try:
            for remote_path in remote_paths:
                try:
                    # Convert user path to real filesystem path
                    real_path = self._to_real_path(remote_path)
                    content = self.file_system.get(real_path)
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    content_b64 = base64.b64encode(content).decode('ascii')
                    results.append({"path": remote_path, "content": content_b64, "success": True})  # Return virtual path
                except Exception as e:
                    results.append({"path": remote_path, "success": False, "error": str(e)})
            
            success_count = sum(1 for r in results if r['success'])
            return {"results": results, "success_count": success_count, "total": len(remote_paths)}
        except Exception as e:
            raise RuntimeError(f"get_file_batch failed: {e}")
    
    def _cmd_get_to_local(self, remote_path: str, local_path: str) -> dict:
        """Handle get_to_local command - download file to specified local path.
        
        This command downloads a file from device directly to a local path,
        bypassing UDP size limits by writing directly to disk.
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(remote_path)
            self.file_system.get(real_path, local_path)
            return {"downloaded": remote_path, "local_path": local_path, "success": True}  # Return virtual path
        except Exception as e:
            raise RuntimeError(f"get_to_local failed: {e}")
    
    def _cmd_put_from_local(self, local_path: str, remote_path: str) -> dict:
        """Handle put_from_local command - upload file from local path.
        
        This command uploads a file from local path directly to device,
        bypassing UDP size limits.
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        import os as os_module
        if not os_module.path.exists(local_path):
            raise RuntimeError(f"Local file not found: {local_path}")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(remote_path)
            self.file_system.put(local_path, real_path)
            return {"uploaded": remote_path, "local_path": local_path, "success": True}  # Return virtual path
        except Exception as e:
            raise RuntimeError(f"put_from_local failed: {e}")
    
    def _cmd_getdir_to_local(self, remote_path: str, local_path: str) -> dict:
        """Handle getdir_to_local command - download directory recursively.
        
        Downloads entire directory from device to local path, preserving directory structure.
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        import os as os_module
        import posixpath
        
        try:
            # Convert user path to real filesystem path
            real_remote_path = self._to_real_path(remote_path)
            
            # Normalize remote path
            real_remote_path = real_remote_path.rstrip('/')
            if not real_remote_path:
                real_remote_path = self.device_root_fs.rstrip('/')
            
            # Create local directory if needed
            os_module.makedirs(local_path, exist_ok=True)
            
            # Get list of files recursively
            # Note: ls_recursive returns only files, not directories!
            # Format: [[rel_path, size, is_dir], ...] where is_dir is always False
            items = self.file_system.ls_recursive(real_remote_path)
            
            # Get the base directory name (e.g., "lib" from "/flash/lib")
            base_name = posixpath.basename(real_remote_path) if real_remote_path != self.device_root_fs.rstrip('/') else ''
            
            files_downloaded = 0
            for item in items:
                rel_path, size, is_dir = item
                
                # rel_path from ls_recursive is like "lib/ticle/ext/__init__.mpy"
                # when called with "/lib", the result has paths like "lib/ticle/..."
                # We need to extract just the part after the base directory name
                
                if base_name and rel_path.startswith(base_name + '/'):
                    # Remove the base directory prefix (e.g., "lib/ticle/..." -> "ticle/...")
                    relative = rel_path[len(base_name) + 1:]
                elif base_name and rel_path == base_name:
                    relative = ''
                else:
                    # Path doesn't have the expected prefix, use as-is
                    relative = rel_path
                
                # Construct local file path
                if relative:
                    local_file = os_module.path.join(local_path, relative.replace('/', os_module.sep))
                else:
                    local_file = os_module.path.join(local_path, posixpath.basename(rel_path))
                
                # Ensure parent directory exists
                parent_dir = os_module.path.dirname(local_file)
                if parent_dir:
                    os_module.makedirs(parent_dir, exist_ok=True)
                
                # Download file - construct full remote path
                if rel_path.startswith('/'):
                    remote_file = rel_path
                else:
                    # rel_path is like "lib/ticle/...", need to make it absolute
                    remote_file = '/' + rel_path
                
                self.file_system.get(remote_file, local_file)
                files_downloaded += 1
            
            return {
                "downloaded_dir": remote_path, 
                "local_path": local_path, 
                "files_count": files_downloaded,
                "success": True
            }
        except Exception as e:
            raise RuntimeError(f"getdir_to_local failed: {e}")
    
    def _cmd_getdir_to_local_streaming(self, seq: int, client_addr: tuple, remote_path: str, local_path: str):
        """Handle getdir_to_local command with streaming progress.
        
        Downloads directory from device to local path, streaming progress updates.
        """
        import threading
        
        def download_thread():
            try:
                if not self.file_system:
                    error_response = AgentProtocol.create_response(seq=seq, error="Not connected")
                    error_data = AgentProtocol.encode_message(error_response)
                    self.server_socket.sendto(error_data, client_addr)
                    return
                
                import os as os_module
                import posixpath
                
                # Send ACK first
                ack_msg = AgentProtocol.create_ack(seq)
                ack_data = AgentProtocol.encode_message(ack_msg)
                self.server_socket.sendto(ack_data, client_addr)
                
                # Convert user path to real filesystem path and normalize
                real_remote_path = self._to_real_path(remote_path)
                remote_normalized = real_remote_path.rstrip('/')
                if not remote_normalized:
                    remote_normalized = self.device_root_fs.rstrip('/')
                
                # Create local directory if needed
                os_module.makedirs(local_path, exist_ok=True)
                
                # Get list of files recursively
                # Note: ls_recursive returns only files, not directories!
                # Format: [[rel_path, size, is_dir], ...] where is_dir is always False
                items = self.file_system.ls_recursive(remote_normalized)
                
                # All items are files (ls_recursive doesn't include directories)
                file_items = items  # All items are files
                total_files = len(file_items)
                
                # Send initial progress (total count)
                progress_msg = AgentProtocol.create_progress_stream(seq, {
                    "current": 0,
                    "total": total_files,
                    "status": "starting"
                })
                progress_data = AgentProtocol.encode_message(progress_msg)
                self.server_socket.sendto(progress_data, client_addr)
                
                files_downloaded = 0
                
                # Download files with progress updates
                for item in file_items:
                    rel_path, size, is_dir = item
                    
                    # rel_path from ls_recursive is like "lib/ticle/ext/__init__.mpy"
                    # when called with "/flash/lib", the result has paths like "lib/ticle/..."
                    # We need to extract just the part after the base directory name
                    
                    # Get the base directory name (e.g., "lib" from "/flash/lib")
                    base_name = posixpath.basename(remote_normalized) if remote_normalized != self.device_root_fs.rstrip('/') else ''
                    
                    if base_name and rel_path.startswith(base_name + '/'):
                        # Remove the base directory prefix (e.g., "lib/ticle/..." -> "ticle/...")
                        relative = rel_path[len(base_name) + 1:]
                    elif base_name and rel_path == base_name:
                        relative = ''
                    else:
                        # Path doesn't have the expected prefix, use as-is
                        relative = rel_path
                    
                    # Construct local file path
                    if relative:
                        local_file = os_module.path.join(local_path, relative.replace('/', os_module.sep))
                    else:
                        local_file = os_module.path.join(local_path, posixpath.basename(rel_path))
                    
                    # Ensure parent directory exists
                    parent_dir = os_module.path.dirname(local_file)
                    if parent_dir:
                        os_module.makedirs(parent_dir, exist_ok=True)
                    
                    # Download file - construct full remote path
                    if rel_path.startswith('/'):
                        remote_file = rel_path
                    else:
                        # rel_path is like "lib/ticle/...", need to make it absolute
                        remote_file = '/' + rel_path
                    
                    self.file_system.get(remote_file, local_file)
                    files_downloaded += 1
                    
                    # Send progress update
                    progress_msg = AgentProtocol.create_progress_stream(seq, {
                        "current": files_downloaded,
                        "total": total_files,
                        "file": posixpath.basename(rel_path),
                        "status": "downloading"
                    })
                    progress_data = AgentProtocol.encode_message(progress_msg)
                    self.server_socket.sendto(progress_data, client_addr)
                
                # Send final response
                final_response = AgentProtocol.create_response(seq=seq, result={
                    "downloaded_dir": remote_path,
                    "local_path": local_path,
                    "files_count": files_downloaded,
                    "success": True
                })
                final_data = AgentProtocol.encode_message(final_response)
                self.server_socket.sendto(final_data, client_addr)
                
            except Exception as e:
                error_response = AgentProtocol.create_response(seq=seq, error=f"getdir_to_local failed: {e}")
                error_data = AgentProtocol.encode_message(error_response)
                self.server_socket.sendto(error_data, client_addr)
        
        # Start download in separate thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def _cmd_putdir_from_local(self, local_path: str, remote_path: str) -> dict:
        """Handle putdir_from_local command - upload directory recursively.
        
        Uploads entire local directory to device.
        """
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        import os as os_module
        
        if not os_module.path.exists(local_path) or not os_module.path.isdir(local_path):
            raise RuntimeError(f"Local directory not found: {local_path}")
        
        try:
            # Convert user path to real filesystem path
            real_remote_path = self._to_real_path(remote_path)
            
            files_uploaded = 0
            
            for root, dirs, files in os_module.walk(local_path):
                # Get relative path from local_path
                rel_root = os_module.path.relpath(root, local_path)
                if rel_root == '.':
                    remote_dir = real_remote_path
                else:
                    remote_dir = real_remote_path.rstrip('/') + '/' + rel_root.replace('\\', '/')
                
                # Create directories on device
                for d in dirs:
                    dir_path = remote_dir.rstrip('/') + '/' + d
                    try:
                        self.file_system.mkdir(dir_path)
                    except:
                        pass  # Directory may already exist
                
                # Upload files
                for f in files:
                    local_file = os_module.path.join(root, f)
                    remote_file = remote_dir.rstrip('/') + '/' + f
                    self.file_system.put(local_file, remote_file)
                    files_uploaded += 1
            
            return {
                "uploaded_dir": remote_path,  # Return virtual path
                "local_path": local_path, 
                "files_count": files_uploaded,
                "success": True
            }
        except Exception as e:
            raise RuntimeError(f"putdir_from_local failed: {e}")
    
    def _cmd_put_from_local_streaming(self, seq: int, client_addr: tuple, local_path: str, remote_path: str):
        """Handle put_from_local command with streaming progress for large files.
        
        Uploads a single file with byte-level progress updates.
        """
        import threading
        
        def upload_thread():
            try:
                if not self.file_system:
                    error_response = AgentProtocol.create_response(seq=seq, error="Not connected")
                    error_data = AgentProtocol.encode_message(error_response)
                    self.server_socket.sendto(error_data, client_addr)
                    return
                
                import os as os_module
                
                if not os_module.path.exists(local_path):
                    error_response = AgentProtocol.create_response(seq=seq, error=f"Local file not found: {local_path}")
                    error_data = AgentProtocol.encode_message(error_response)
                    self.server_socket.sendto(error_data, client_addr)
                    return
                
                # Send ACK first
                ack_msg = AgentProtocol.create_ack(seq)
                ack_data = AgentProtocol.encode_message(ack_msg)
                self.server_socket.sendto(ack_data, client_addr)
                
                # Get file size
                file_size = os_module.path.getsize(local_path)
                file_name = os_module.path.basename(local_path)
                
                # Send initial progress
                progress_msg = AgentProtocol.create_progress_stream(seq, {
                    "current": 0,
                    "total": file_size,
                    "file": file_name,
                    "status": "starting"
                })
                progress_data = AgentProtocol.encode_message(progress_msg)
                self.server_socket.sendto(progress_data, client_addr)
                
                # Convert user path to real filesystem path
                real_remote_path = self._to_real_path(remote_path)
                
                # Upload file with progress callback
                bytes_uploaded = [0]  # Use list for closure
                last_progress_time = [time.time()]
                
                def progress_callback(bytes_sent: int, total_bytes: int):
                    bytes_uploaded[0] = bytes_sent
                    # Send progress updates at most every 100ms to avoid UDP flood
                    now = time.time()
                    if now - last_progress_time[0] >= 0.1:
                        last_progress_time[0] = now
                        progress_msg = AgentProtocol.create_progress_stream(seq, {
                            "current": bytes_sent,
                            "total": total_bytes,
                            "file": file_name,
                            "status": "uploading"
                        })
                        progress_data = AgentProtocol.encode_message(progress_msg)
                        self.server_socket.sendto(progress_data, client_addr)
                
                # Use put with progress callback
                self.file_system.put(local_path, real_remote_path, progress_callback=progress_callback)
                bytes_uploaded[0] = file_size
                
                # Send final response
                final_response = AgentProtocol.create_response(seq=seq, result={
                    "uploaded": remote_path,  # Return virtual path
                    "local_path": local_path,
                    "bytes": bytes_uploaded[0],
                    "success": True
                })
                final_data = AgentProtocol.encode_message(final_response)
                self.server_socket.sendto(final_data, client_addr)
                
            except Exception as e:
                error_response = AgentProtocol.create_response(seq=seq, error=str(e))
                error_data = AgentProtocol.encode_message(error_response)
                try:
                    self.server_socket.sendto(error_data, client_addr)
                except:
                    pass
            finally:
                # Clear busy flag
                with self._repl_busy_lock:
                    self._repl_busy = False
                    self._repl_busy_client = None
        
        # Start upload in separate thread
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
    
    def _cmd_putdir_from_local_streaming(self, seq: int, client_addr: tuple, local_path: str, remote_path: str):
        """Handle putdir_from_local command with streaming progress.
        
        Uploads directory from local path to device, streaming progress updates.
        Uses batch mode (single REPL session) to avoid timing issues.
        """
        import threading
        import posixpath
        
        # Directories and file patterns to exclude
        EXCLUDE_DIRS = {'__pycache__', '.git', '.svn', '.hg', 'node_modules', '.venv', 'venv', '__MACOSX'}
        EXCLUDE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib'}
        
        def upload_thread():
            try:
                if not self.file_system:
                    error_response = AgentProtocol.create_response(seq=seq, error="Not connected")
                    error_data = AgentProtocol.encode_message(error_response)
                    self.server_socket.sendto(error_data, client_addr)
                    return
                
                import os as os_module
                
                if not os_module.path.exists(local_path) or not os_module.path.isdir(local_path):
                    error_response = AgentProtocol.create_response(seq=seq, error=f"Local directory not found: {local_path}")
                    error_data = AgentProtocol.encode_message(error_response)
                    self.server_socket.sendto(error_data, client_addr)
                    return
                
                # Send ACK first
                ack_msg = AgentProtocol.create_ack(seq)
                ack_data = AgentProtocol.encode_message(ack_msg)
                self.server_socket.sendto(ack_data, client_addr)
                
                base_local = os_module.path.abspath(local_path)
                # Convert user path to real filesystem path
                real_remote_path = self._to_real_path(remote_path)
                base_remote = real_remote_path.replace("\\", "/")
                
                # Collect all files and create directories first
                file_specs = []
                dirs_to_create = set()
                
                for parent, child_dirs, child_files in os_module.walk(base_local, followlinks=True):
                    # Filter out excluded directories (modifying in-place affects os.walk)
                    child_dirs[:] = [d for d in child_dirs if d not in EXCLUDE_DIRS]
                    
                    rel = os_module.path.relpath(parent, base_local).replace("\\", "/")
                    remote_parent = posixpath.normpath(
                        posixpath.join(base_remote, "" if rel == "." else rel)
                    )
                    
                    # Collect directories to create
                    dirs_to_create.add(remote_parent)
                    
                    for filename in child_files:
                        # Skip excluded file extensions
                        _, ext = os_module.path.splitext(filename)
                        if ext.lower() in EXCLUDE_EXTENSIONS:
                            continue
                        
                        local_file = os_module.path.join(parent, filename)
                        remote_file = posixpath.join(remote_parent, filename).replace("\\", "/")
                        file_specs.append((local_file, remote_file, filename))
                
                total_files = len(file_specs)
                
                # Send initial progress (total count)
                progress_msg = AgentProtocol.create_progress_stream(seq, {
                    "current": 0,
                    "total": total_files,
                    "status": "starting"
                })
                progress_data = AgentProtocol.encode_message(progress_msg)
                self.server_socket.sendto(progress_data, client_addr)
                
                # Create directories first (outside the batch upload session)
                for dir_path in sorted(dirs_to_create):
                    try:
                        self.file_system.mkdir(dir_path)
                    except:
                        pass  # Directory may already exist
                
                # Use batch progress callback to send streaming updates
                def progress_callback(done: int, total: int, filename: str):
                    progress_msg = AgentProtocol.create_progress_stream(seq, {
                        "current": done,
                        "total": total,
                        "file": filename,
                        "status": "uploading" if done < total else "complete"
                    })
                    progress_data = AgentProtocol.encode_message(progress_msg)
                    self.server_socket.sendto(progress_data, client_addr)
                
                # Use batch mode (single session) for all files
                batch_specs = [(local_file, remote_file) for local_file, remote_file, _ in file_specs]
                self.repl_protocol.put_files_batch(batch_specs, progress_callback)
                
                # Send final response
                final_response = AgentProtocol.create_response(seq=seq, result={
                    "uploaded_dir": remote_path,
                    "local_path": local_path,
                    "files_count": total_files,
                    "success": True
                })
                final_data = AgentProtocol.encode_message(final_response)
                self.server_socket.sendto(final_data, client_addr)
                
            except Exception as e:
                error_response = AgentProtocol.create_response(seq=seq, error=str(e))
                error_data = AgentProtocol.encode_message(error_response)
                try:
                    self.server_socket.sendto(error_data, client_addr)
                except:
                    pass
            finally:
                # Clear busy flag
                with self._repl_busy_lock:
                    self._repl_busy = False
                    self._repl_busy_client = None
        
        # Start upload in separate thread
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
    
    def _cmd_ls_recursive(self, path: str = "/") -> dict:
        """Handle ls_recursive command - list directory recursively."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            items = self.file_system.ls_recursive(real_path)
            # Convert real paths back to virtual paths
            return {
                "items": [{"name": self._to_virtual_path(n), "size": s, "is_dir": d} for n, s, d in items],
                "path": path  # Return virtual path
            }
        except Exception as e:
            raise RuntimeError(f"ls_recursive failed: {e}")
    
    def _cmd_cp(self, source: str, dest: str, recursive: bool = False) -> dict:
        """Handle cp command - copy file or directory on device."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user paths to real filesystem paths
            real_source = self._to_real_path(source)
            real_dest = self._to_real_path(dest)
            
            # Check if source is a directory
            is_source_dir = self.file_system.is_dir(real_source)
            
            if is_source_dir and not recursive:
                raise RuntimeError(f"cp: {source} is a directory (use -r to copy recursively)")
            
            if is_source_dir:
                # Copy directory recursively
                items = self.file_system.ls_recursive(real_source)
                success_count = 0
                
                for rel_path, size, is_dir in items:
                    if is_dir:
                        continue
                    
                    # Construct paths (using real paths for operations)
                    src_file = real_source.rstrip('/') + '/' + rel_path
                    dest_file = real_dest.rstrip('/') + '/' + rel_path
                    
                    # Create destination directory
                    dest_dir = '/'.join(dest_file.split('/')[:-1])
                    try:
                        self.file_system.mkdir(dest_dir)
                    except:
                        pass
                    
                    # Copy file using REPL command
                    command = f"""
with open('{src_file}', 'rb') as src:
    with open('{dest_file}', 'wb') as dst:
        while True:
            chunk = src.read(512)
            if not chunk:
                break
            dst.write(chunk)
"""
                    self.repl_protocol.exec(command)
                    success_count += 1
                
                return {"copied": True, "source": source, "dest": dest, "files_count": success_count}  # Return virtual paths
            else:
                # Copy single file
                # Check if dest is a directory
                try:
                    if self.file_system.is_dir(real_dest):
                        import posixpath
                        real_dest = posixpath.join(real_dest, posixpath.basename(real_source))
                except:
                    pass
                
                command = f"""
with open('{real_source}', 'rb') as src:
    with open('{real_dest}', 'wb') as dst:
        while True:
            chunk = src.read(512)
            if not chunk:
                break
            dst.write(chunk)
"""
                self.repl_protocol.exec(command)
                return {"copied": True, "source": source, "dest": dest}  # Return virtual paths
        except Exception as e:
            raise RuntimeError(f"cp failed: {e}")
    
    def _cmd_mv(self, source: str, dest: str) -> dict:
        """Handle mv command - move/rename file or directory on device."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user paths to real filesystem paths
            real_source = self._to_real_path(source)
            real_dest = self._to_real_path(dest)
            
            # Use os.rename for atomic move
            command = f"""
import os
os.rename('{real_source}', '{real_dest}')
"""
            self.repl_protocol.exec(command)
            return {"moved": True, "source": source, "dest": dest}  # Return virtual paths
        except Exception as e:
            raise RuntimeError(f"mv failed: {e}")
    
    def _cmd_stat(self, path: str) -> dict:
        """Handle stat command - get file/directory information."""
        if not self.file_system:
            raise RuntimeError("Not connected")
        
        try:
            # Convert user path to real filesystem path
            real_path = self._to_real_path(path)
            size = self.file_system.state(real_path)
            is_dir = self.file_system.is_dir(real_path)
            return {
                "path": path,  # Return virtual path
                "size": size,
                "is_dir": is_dir
            }
        except Exception as e:
            raise RuntimeError(f"stat failed: {e}")
    
    def _repl_reader_loop(self):
        """Background thread that reads device output and buffers it."""
        transport = self.repl_protocol.transport
        while self._repl_session_active and self.repl_protocol:
            try:
                count = transport.in_waiting()
                if count > 0:
                    data = transport.read(count)
                    if data:
                        with self._repl_buffer_lock:
                            self._repl_output_buffer += data
                else:
                    time.sleep(0.01)
            except Exception:
                break
    
    def _cmd_repl_enter(self) -> dict:
        """Enter Friendly REPL mode and start background reader thread."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        # Stop existing session if any
        if self._repl_session_active:
            self._repl_session_active = False
            if self._repl_reader_thread:
                self._repl_reader_thread.join(timeout=1)
        
        transport = self.repl_protocol.transport
        
        # Exit Raw REPL if we're in it
        if self.repl_protocol._in_raw_repl:
            try:
                self.repl_protocol._leave_repl()
            except:
                pass
        
        # Send Ctrl+B to ensure Friendly REPL, then Ctrl+C to interrupt
        transport.write(b'\x02')  # Ctrl+B - exit raw repl / show banner
        time.sleep(0.05)
        transport.write(b'\x03')  # Ctrl+C - interrupt any running code
        time.sleep(0.1)
        
        # Drain any pending output
        drain_start = time.time()
        while time.time() - drain_start < 0.3:
            if transport.in_waiting() > 0:
                transport.read(transport.in_waiting())
                time.sleep(0.02)
            else:
                break
        
        # Clear buffer
        with self._repl_buffer_lock:
            self._repl_output_buffer = b""
        
        # Send newline to get fresh prompt
        transport.write(b'\r')
        time.sleep(0.15)
        
        # Read response and check for prompt
        response = b""
        read_start = time.time()
        while time.time() - read_start < 0.5:
            if transport.in_waiting() > 0:
                response += transport.read(transport.in_waiting())
                if b'>>>' in response:
                    break
            time.sleep(0.02)
        
        response_str = response.decode('utf-8', errors='replace')
        prompt_found = '>>>' in response_str
        
        if prompt_found:
            # Start background reader thread
            self._repl_session_active = True
            self._repl_reader_thread = threading.Thread(
                target=self._repl_reader_loop, 
                daemon=True, 
                name='REPL-Reader'
            )
            self._repl_reader_thread.start()
        
        return {
            "entered": prompt_found,
            "output": response_str
        }
    
    def _cmd_repl_exit(self) -> dict:
        """Exit REPL session (stop background reader)."""
        self._repl_session_active = False
        if self._repl_reader_thread:
            self._repl_reader_thread.join(timeout=1)
            self._repl_reader_thread = None
        
        with self._repl_buffer_lock:
            self._repl_output_buffer = b""
        
        return {"exited": True}
    
    def _cmd_repl_write(self, data: str) -> dict:
        """Write data to the Friendly REPL."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        transport = self.repl_protocol.transport
        
        # Convert string to bytes and write
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        transport.write(data)
        return {"written": len(data)}
    
    def _cmd_repl_read(self) -> dict:
        """Read buffered output from the REPL session."""
        if not self.repl_protocol:
            raise RuntimeError("Not connected")
        
        # Get buffered data
        with self._repl_buffer_lock:
            data = self._repl_output_buffer
            self._repl_output_buffer = b""
        
        return {
            "output": data.decode('utf-8', errors='replace')
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.running = False
        
        # Stop detached script if running (drain thread + Ctrl+C)
        if self._run_detached:
            self._stop_detached_script()
        
        # Stop REPL session
        self._repl_session_active = False
        if self._repl_reader_thread:
            self._repl_reader_thread.join(timeout=1)
        
        if self.repl_protocol:
            try:
                self._cmd_free()
            except Exception:
                pass
        
        if self.server_socket:
            self.server_socket.close()
        
        # Wait for heartbeat thread to finish
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=2)
        
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
        
        print("replx agent stopped")


def main():
    """Entry point for agent server."""
    # Parse port from command line: python -m replx.agent.server [port]
    port = None
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
    
    server = AgentServer(port=port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.cleanup()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

