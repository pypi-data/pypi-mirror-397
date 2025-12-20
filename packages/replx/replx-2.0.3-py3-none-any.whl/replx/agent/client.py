"""Agent client for communicating with agent server via UDP."""

import os
import sys
import socket
import tempfile
import time
from typing import Dict, Any, Optional, Callable

from .protocol import AgentProtocol


class AgentClient:
    """Client for communicating with replx agent."""
    
    DEFAULT_AGENT_PORT = 49152  # Default port, can be overridden
    AGENT_HOST = '127.0.0.1'
    TIMEOUT = 5.0  # seconds
    MAX_RETRIES = 3
    
    def __init__(self, port: int = None):
        """Initialize agent client."""
        self.agent_port = port or self.DEFAULT_AGENT_PORT
        self.sock: Optional[socket.socket] = None
    
    def connect(self):
        """Create UDP socket (no actual connection needed)."""
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(self.TIMEOUT)
    
    def disconnect(self):
        """Close socket."""
        if self.sock:
            self.sock.close()
            self.sock = None
    
    def send_command(self, command: str, timeout: float = None, **args) -> Dict[str, Any]:
        """Send a command to the agent and return response."""
        if not self.sock:
            self.connect()
        
        effective_timeout = timeout if timeout else self.TIMEOUT
        
        if timeout:
            self.sock.settimeout(timeout)
        
        # Create request with sequence number
        request = AgentProtocol.create_request(command, **args)
        seq = request['seq']
        request_data = AgentProtocol.encode_message(request)
        
        ack_received = False
        response = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # Send request
                self.sock.sendto(request_data, (self.AGENT_HOST, self.agent_port))
                
                # Wait for ACK or response
                start_time = time.time()
                while time.time() - start_time < effective_timeout:
                    try:
                        data, addr = self.sock.recvfrom(AgentProtocol.MAX_UDP_SIZE)
                        
                        msg = AgentProtocol.decode_message(data)
                        if not msg or msg.get('seq') != seq:
                            continue
                        
                        if msg.get('type') == 'ack':
                            ack_received = True
                            # Continue waiting for response
                            continue
                        
                        if msg.get('type') == 'response':
                            response = msg
                            break
                    
                    except socket.timeout:
                        break
                
                if response:
                    break
                
                # No response, retry (only if not using short timeout)
                if attempt < self.MAX_RETRIES - 1 and effective_timeout >= 1.0:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
            
            except socket.timeout:
                if attempt < self.MAX_RETRIES - 1:
                    continue
                raise RuntimeError(f"Agent timeout after {self.MAX_RETRIES} attempts")
        
        if not response:
            raise RuntimeError("No response from agent")
        
        if response.get('error'):
            raise RuntimeError(response['error'])
        
        return response.get('result', {})
    
    def run_interactive(self, script_path: str = None, script_content: str = None,
                        echo: bool = False,
                        output_callback: Callable[[bytes, str], None] = None,
                        input_provider: Callable[[], Optional[bytes]] = None,
                        stop_check: Callable[[], bool] = None) -> Dict[str, Any]:
        """Run script interactively with push-based streaming.
        
        Server pushes output directly via UDP 'stream' messages.
        Client only receives - no polling required.
        """
        if not self.sock:
            self.connect()
        
        # Send run_interactive request to start execution
        request = AgentProtocol.create_request(
            'run_interactive',
            script_path=script_path,
            script_content=script_content,
            echo=echo
        )
        seq = request['seq']
        request_data = AgentProtocol.encode_message(request)
        
        # Send request
        self.sock.sendto(request_data, (self.AGENT_HOST, self.agent_port))
        
        # Wait for ACK
        self.sock.settimeout(5.0)
        ack_received = False
        start_time = time.time()
        
        while time.time() - start_time < 5.0:
            try:
                data, addr = self.sock.recvfrom(AgentProtocol.MAX_UDP_SIZE)
                msg = AgentProtocol.decode_message(data)
                if msg and msg.get('seq') == seq and msg.get('type') == 'ack':
                    ack_received = True
                    break
            except socket.timeout:
                break
        
        if not ack_received:
            raise RuntimeError("No ACK from agent - run_interactive failed to start")
        
        # Push-based receiving: just listen for stream messages from server
        self.sock.settimeout(0.01)  # 10ms timeout for responsive input handling
        input_interval = 0.001  # 1ms input check
        last_input_time = 0
        
        try:
            while True:
                # Check for stop request
                if stop_check and stop_check():
                    try:
                        self.send_command('run_stop', timeout=0.5)
                    except Exception:
                        pass
                    break
                
                now = time.time()
                
                # Check input
                if now - last_input_time >= input_interval:
                    last_input_time = now
                    if input_provider:
                        try:
                            input_data = input_provider()
                            if input_data:
                                input_msg = AgentProtocol.create_input(seq, input_data)
                                input_data_encoded = AgentProtocol.encode_message(input_msg)
                                self.sock.sendto(input_data_encoded, (self.AGENT_HOST, self.agent_port))
                        except Exception:
                            pass
                
                # Receive stream messages from server (non-blocking with short timeout)
                try:
                    data, addr = self.sock.recvfrom(AgentProtocol.MAX_UDP_SIZE)
                    msg = AgentProtocol.decode_message(data)
                    
                    if msg and msg.get('type') == 'stream':
                        # Handle streamed output
                        output = msg.get('output', '')
                        if output and output_callback:
                            output_callback(output.encode('utf-8'), 'stdout')
                        
                        # Check for completion
                        if msg.get('completed'):
                            error = msg.get('error')
                            if error and output_callback:
                                output_callback(error.encode('utf-8'), 'stderr')
                            break
                            
                except socket.timeout:
                    pass  # No data available, continue loop
                except Exception:
                    pass
                    
        except KeyboardInterrupt:
            try:
                self.send_command('run_stop', timeout=0.5)
            except Exception:
                pass
            raise
        
        # Restore timeout
        self.sock.settimeout(self.TIMEOUT)
        
        return {"run": True, "completed": True}
    
    def send_command_streaming(self, command: str, timeout: float = None,
                                progress_callback: Callable[[Dict[str, Any]], None] = None,
                                **args) -> Dict[str, Any]:
        """
        Send a command to the agent and handle streaming progress.
        
        :param command: Command name
        :param timeout: Override default timeout
        :param progress_callback: Callback for progress updates
        :param args: Command arguments
        :return: Final response dict
        """
        if not self.sock:
            self.connect()
        
        effective_timeout = timeout if timeout else 60.0  # Longer timeout for streaming ops
        
        # Create request with sequence number
        request = AgentProtocol.create_request(command, **args)
        seq = request['seq']
        request_data = AgentProtocol.encode_message(request)
        
        # Send request
        self.sock.sendto(request_data, (self.AGENT_HOST, self.agent_port))
        
        # Set short timeout for non-blocking receive
        self.sock.settimeout(0.1)
        
        ack_received = False
        response = None
        start_time = time.time()
        
        while time.time() - start_time < effective_timeout:
            try:
                data, addr = self.sock.recvfrom(AgentProtocol.MAX_UDP_SIZE)
                msg = AgentProtocol.decode_message(data)
                
                if not msg or msg.get('seq') != seq:
                    continue
                
                msg_type = msg.get('type')
                
                if msg_type == 'ack':
                    ack_received = True
                    continue
                
                elif msg_type == 'stream':
                    # Handle streaming progress
                    if progress_callback:
                        stream_data = msg.get('data', {})
                        progress_callback(stream_data)
                    continue
                
                elif msg_type == 'response':
                    response = msg
                    break
                
            except socket.timeout:
                # No data available, continue waiting
                if not ack_received and time.time() - start_time > 5.0:
                    raise RuntimeError("No response from agent")
                continue
            except Exception as e:
                raise RuntimeError(f"Communication error: {e}")
        
        # Restore timeout
        self.sock.settimeout(self.TIMEOUT)
        
        if not response:
            raise RuntimeError("No response from agent (timeout)")
        
        if response.get('error'):
            raise RuntimeError(response['error'])
        
        return response.get('result', {})
    
    def ping(self) -> bool:
        """
        Ping agent to check if it's alive.
        Returns True if agent responds, False otherwise.
        """
        try:
            result = self.send_command('ping', timeout=1.0)
            return result.get('pong', False)
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    @staticmethod
    def is_agent_running(port: int = None) -> bool:
        """Check if agent is running by pinging it."""
        try:
            client = AgentClient(port=port)
            return client.ping()
        except Exception:
            return False
    
    @staticmethod
    def start_agent(port: int = None, background: bool = True) -> bool:
        """
        Start the agent in the background.
        Returns True if started successfully, False if already running.
        
        :param port: Agent port (default: DEFAULT_AGENT_PORT)
        :param background: If True, start as background process (default)
        """
        if AgentClient.is_agent_running(port=port):
            return False
        
        # Start agent as subprocess with port argument
        import subprocess
        python_exe = sys.executable
        agent_module = 'replx.agent.server'
        
        # Build command with port if specified
        cmd = [python_exe, '-m', agent_module]
        if port:
            cmd.append(str(port))
        
        if background:
            if sys.platform == 'win32':
                # Windows: start detached process
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
                
                subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    startupinfo=startupinfo
                )
            else:
                # Unix: start agent process
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
        else:
            # Start in foreground (for debugging)
            subprocess.Popen(cmd)
        
        # Wait for agent to start
        for i in range(30):  # Wait up to 3 seconds
            time.sleep(0.1)
            if AgentClient.is_agent_running(port=port):
                return True
        
        raise RuntimeError("Failed to start agent (timeout)")
    
    @staticmethod
    def stop_agent(port: int = None, timeout: float = 3.0) -> bool:
        """
        Stop the agent gracefully, with force kill fallback.
        Returns True if stopped, False if not running.
        
        :param port: Agent port (default: DEFAULT_AGENT_PORT)
        :param timeout: Seconds to wait for graceful shutdown before force kill
        """
        if not AgentClient.is_agent_running(port=port):
            return False
        
        try:
            # Send shutdown command
            client = AgentClient(port=port)
            client.send_command('shutdown', timeout=1.0)
        except Exception:
            pass  # Agent may not respond, continue to wait/kill
        
        # Wait for agent to stop gracefully
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.1)
            if not AgentClient.is_agent_running(port=port):
                return True
        
        # Agent didn't stop gracefully - force kill using PID file
        effective_port = port or AgentClient.DEFAULT_AGENT_PORT
        pid_file = os.path.join(tempfile.gettempdir(), f'replx_agent_{effective_port}.pid')
        
        try:
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                if sys.platform == 'win32':
                    os.system(f'taskkill /F /PID {pid} >nul 2>&1')
                else:
                    import signal
                    os.kill(pid, signal.SIGKILL)
                os.remove(pid_file)
        except Exception:
            pass
        
        # Final check
        time.sleep(0.2)
        return not AgentClient.is_agent_running(port=port)
