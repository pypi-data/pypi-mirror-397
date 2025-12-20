from replx import __version__

import os 
import sys
import time
import re
import json
import threading
import posixpath
import shutil
import tempfile
import glob
import shlex
import fnmatch
import hashlib
import subprocess
import urllib.request
import urllib.error
import signal
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console

from serial.tools.list_ports import comports as list_ports_comports
from rich.live import Live

from ..exceptions import ProtocolError
from ..terminal import (
    IS_WINDOWS,
    getch,
)
from .helpers import (
    OutputHelper, DeviceScanner, DeviceValidator, NetworkScanner,
    EnvironmentManager, StoreManager, CompilerHelper, InstallHelper,
    SearchHelper, UpdateChecker, RegistryHelper,
    set_global_context, get_panel_box, CONSOLE_WIDTH
)
from ..protocol import ReplProtocol
from ..agent import AgentClient

import typer.rich_utils

def _preprocess_cli_aliases():
    """Transform CLI aliases into subcommand format."""
    if len(sys.argv) < 2:
        return
    
    first_arg = sys.argv[1]
    
    if first_arg in ("-v", "--version"):
        sys.argv[1] = "version"
    
    elif first_arg in ("-c", "--command"):
        sys.argv[1] = "exec"

_preprocess_cli_aliases()

@dataclass
class RuntimeState:
    version: str = "?"
    core: str = ""
    device: str = ""
    device_root_fs: str = "/"
    core_path: str = ""
    device_path: str = ""

STATE = RuntimeState()

def _find_env_file() -> Optional[str]:
    """Find .vscode/.replx file by searching up from current directory."""
    current = os.getcwd()
    root = os.path.abspath(os.sep)
    
    while current != root:
        env_path = os.path.join(current, ".vscode", ".replx")
        if os.path.exists(env_path):
            return env_path
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None

def _find_or_create_vscode_dir() -> str:
    """Find existing .vscode directory or create one in current directory."""
    current = os.getcwd()
    root = os.path.abspath(os.sep)
    
    search_dir = current
    while search_dir != root:
        vscode_dir = os.path.join(search_dir, ".vscode")
        if os.path.isdir(vscode_dir):
            return vscode_dir
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent
    
    vscode_dir = os.path.join(current, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    return vscode_dir

def _auto_detect_port() -> Optional[str]:
    """Auto-detect the first available MicroPython REPL port."""
    results = DeviceScanner.scan_serial_ports(max_workers=5)
    if results:
        return results[0][0]
    return None

# ============================================================================
# INI-style .replx file management for multi-device support
# ============================================================================

def _read_env_ini(env_path: str) -> dict:
    """
    Read INI-style .replx file with sections for multi-device support.
    
    File format:
        [COM3]
        CORE=RP2350
        DEVICE=ticle
        AGENT_PORT=49152
        
        [192.168.1.10]
        CORE=RP2350
        DEVICE=ticle
        AGENT_PORT=49154
        PASSWORD=mypassword
        
        [DEFAULT]
        CONNECTION=COM3
    
    Returns:
        dict with structure:
        {
            'connections': {
                'COM3': {'core': 'RP2350', 'device': 'ticle', 'agent_port': 49152},
                '192.168.1.10': {'core': 'RP2350', 'device': 'ticle', 'agent_port': 49154, 'password': 'mypassword'}
            },
            'default': 'COM3'
        }
    """
    result = {
        'connections': {},
        'default': None
    }
    
    if not os.path.exists(env_path):
        return result
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_section = None
        
        for line in content.splitlines():
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                if current_section.upper() != 'DEFAULT':
                    result['connections'][current_section] = {}
                continue
            
            # Key=Value pairs
            if '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if current_section.upper() == 'DEFAULT':
                    if key == 'CONNECTION':
                        result['default'] = value
                else:
                    conn = result['connections'][current_section]
                    if key == 'CORE':
                        conn['core'] = value
                    elif key == 'DEVICE':
                        conn['device'] = value
                    elif key == 'AGENT_PORT':
                        try:
                            conn['agent_port'] = int(value)
                        except ValueError:
                            pass
                    elif key == 'PASSWORD':
                        conn['password'] = value
        
        return result
    except Exception:
        return result

def _write_env_ini(env_path: str, connections: dict, default: Optional[str] = None):
    """
    Write INI-style .replx file with sections for multi-device support.
    
    Args:
        env_path: Path to .replx file
        connections: Dict of connection configs
            {'COM3': {'core': 'RP2350', 'device': 'ticle', 'agent_port': 49152}, ...}
        default: Default connection key (e.g., 'COM3')
    """
    lines = []
    
    # Write connection sections
    for conn_key, conn_data in connections.items():
        lines.append(f'[{conn_key}]')
        if conn_data.get('core'):
            lines.append(f"CORE={conn_data['core']}")
        if conn_data.get('device'):
            lines.append(f"DEVICE={conn_data['device']}")
        if conn_data.get('agent_port'):
            lines.append(f"AGENT_PORT={conn_data['agent_port']}")
        if conn_data.get('password'):
            lines.append(f"PASSWORD={conn_data['password']}")
        lines.append('')
    
    # Write DEFAULT section
    if default:
        lines.append('[DEFAULT]')
        lines.append(f'CONNECTION={default}')
        lines.append('')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def _get_connection_config(env_path: str, connection: str) -> Optional[dict]:
    """Get configuration for a specific connection from .replx file."""
    env_data = _read_env_ini(env_path)
    # Case-insensitive lookup for serial ports
    for key, value in env_data['connections'].items():
        if key.upper() == connection.upper():
            return value
    return None

def _update_connection_config(env_path: str, connection: str, core: str = None, 
                              device: str = None, agent_port: int = None, 
                              password: str = None, set_default: bool = False):
    """Update or add a connection configuration in .replx file."""
    env_data = _read_env_ini(env_path)
    
    # Normalize connection key (uppercase for serial ports)
    conn_key = connection.upper() if not '.' in connection else connection
    
    # Find existing connection (case-insensitive)
    existing_key = None
    for key in env_data['connections']:
        if key.upper() == conn_key.upper():
            existing_key = key
            break
    
    if existing_key:
        conn_key = existing_key
    else:
        env_data['connections'][conn_key] = {}
    
    conn = env_data['connections'][conn_key]
    
    if core is not None:
        conn['core'] = core
    if device is not None:
        conn['device'] = device
    # Always store agent_port (use default if None)
    conn['agent_port'] = agent_port if agent_port is not None else DEFAULT_AGENT_PORT
    if password is not None:
        conn['password'] = password
    
    if set_default:
        env_data['default'] = conn_key
    
    _write_env_ini(env_path, env_data['connections'], env_data['default'])

def _get_default_connection(env_path: str) -> Optional[str]:
    """Get the default connection from .replx file."""
    env_data = _read_env_ini(env_path)
    return env_data.get('default')

# ============================================================================
# Session file management for terminal-specific connection tracking
# ============================================================================

def _get_terminal_pid() -> Optional[int]:
    """
    Get the terminal/shell process PID.
    Walks up the process tree to find a shell process (pwsh, powershell, cmd, bash, etc.)
    """
    try:
        if IS_WINDOWS:
            import ctypes
            from ctypes import wintypes
            
            kernel32 = ctypes.windll.kernel32
            
            class PROCESSENTRY32(ctypes.Structure):
                _fields_ = [
                    ('dwSize', wintypes.DWORD),
                    ('cntUsage', wintypes.DWORD),
                    ('th32ProcessID', wintypes.DWORD),
                    ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
                    ('th32ModuleID', wintypes.DWORD),
                    ('cntThreads', wintypes.DWORD),
                    ('th32ParentProcessID', wintypes.DWORD),
                    ('pcPriClassBase', ctypes.c_long),
                    ('dwFlags', wintypes.DWORD),
                    ('szExeFile', ctypes.c_char * 260),
                ]
            
            TH32CS_SNAPPROCESS = 0x00000002
            
            # Shell process names to look for
            shell_names = {b'pwsh.exe', b'powershell.exe', b'cmd.exe', b'bash.exe', b'wsl.exe', b'WindowsTerminal.exe'}
            
            snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            
            # Build process info map
            process_map = {}  # pid -> (parent_pid, exe_name)
            pe32 = PROCESSENTRY32()
            pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
            
            if kernel32.Process32First(snapshot, ctypes.byref(pe32)):
                while True:
                    process_map[pe32.th32ProcessID] = (
                        pe32.th32ParentProcessID,
                        pe32.szExeFile.lower()
                    )
                    if not kernel32.Process32Next(snapshot, ctypes.byref(pe32)):
                        break
            
            kernel32.CloseHandle(snapshot)
            
            # Walk up the process tree
            current_pid = os.getpid()
            visited = set()
            
            while current_pid in process_map and current_pid not in visited:
                visited.add(current_pid)
                parent_pid, exe_name = process_map[current_pid]
                
                # Check if parent is a shell
                if exe_name in shell_names:
                    return parent_pid
                
                current_pid = parent_pid
            
            # Fallback: return immediate parent
            if os.getpid() in process_map:
                return process_map[os.getpid()][0]
            return None
        else:
            return os.getppid()
    except Exception:
        return None

def _get_session_file_path() -> str:
    """Get the session file path for current terminal (based on terminal PID)."""
    terminal_pid = _get_terminal_pid()
    if terminal_pid:
        return os.path.join(tempfile.gettempdir(), f'replx_session_{terminal_pid}.json')
    # Fallback to current PID if terminal PID cannot be determined
    return os.path.join(tempfile.gettempdir(), f'replx_session_{os.getpid()}.json')

def _is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        if IS_WINDOWS:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False

def _read_session() -> Optional[dict]:
    """
    Read session file for current terminal.
    Returns None if session is invalid:
    - Terminal process no longer exists
    - Agent is not running
    - Board is not connected
    
    Returns:
        dict with structure:
        {
            'connection': 'COM3',
            'agent_port': 49152,
            'created': '2025-12-15T10:30:00',
            'terminal_pid': 5678
        }
    """
    session_path = _get_session_file_path()
    
    if not os.path.exists(session_path):
        return None
    
    try:
        with open(session_path, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        # Validate terminal process is still running
        terminal_pid = session.get('terminal_pid') or session.get('parent_pid')  # backward compat
        if terminal_pid and not _is_process_running(terminal_pid):
            # Terminal process no longer exists, session is orphaned
            _delete_session()
            return None
        
        # Validate agent is running and board is connected
        agent_port = session.get('agent_port')
        if agent_port:
            if not AgentClient.is_agent_running(port=agent_port):
                # Agent not running, session is stale
                _delete_session()
                return None
            
            # Check if board is actually connected
            try:
                with AgentClient(port=agent_port) as client:
                    status = client.send_command('status', timeout=1.0)
                    if not status.get('connected', False):
                        # Board disconnected, session is stale
                        _delete_session()
                        return None
            except Exception:
                # Cannot verify connection, session is likely stale
                _delete_session()
                return None
        
        return session
    except Exception:
        return None

def _write_session(connection: str, agent_port: int):
    """Write session file for current terminal."""
    import datetime
    
    session = {
        'connection': connection,
        'agent_port': agent_port,
        'created': datetime.datetime.now().isoformat(),
        'terminal_pid': _get_terminal_pid()
    }
    
    session_path = _get_session_file_path()
    
    try:
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2)
    except Exception:
        pass

def _delete_session():
    """Delete session file for current terminal."""
    session_path = _get_session_file_path()
    try:
        if os.path.exists(session_path):
            os.remove(session_path)
    except Exception:
        pass

def _list_all_sessions() -> list:
    """
    List all session files in temp directory.
    
    Returns:
        List of dicts with session info and validity status.
        A session is valid only if:
        1. Terminal process is still running
        2. Agent is running on the registered port
        3. Agent has an active board connection
    """
    sessions = []
    temp_dir = tempfile.gettempdir()
    
    for filename in os.listdir(temp_dir):
        if filename.startswith('replx_session_') and filename.endswith('.json'):
            filepath = os.path.join(temp_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                
                # Extract PID from filename
                pid = int(filename.replace('replx_session_', '').replace('.json', ''))
                
                # Check if terminal process is still running (backward compat with parent_pid)
                terminal_pid = session.get('terminal_pid') or session.get('parent_pid')
                terminal_running = terminal_pid and _is_process_running(terminal_pid)
                
                # Check if agent is running and board is connected
                agent_port = session.get('agent_port')
                agent_running = False
                board_connected = False
                
                if terminal_running and agent_port:
                    agent_running = AgentClient.is_agent_running(port=agent_port)
                    if agent_running:
                        # Verify board is actually connected via status command
                        try:
                            with AgentClient(port=agent_port) as client:
                                status = client.send_command('status', timeout=1.0)
                                board_connected = status.get('connected', False)
                        except Exception:
                            board_connected = False
                
                # Session is valid only if all conditions are met
                is_valid = terminal_running and agent_running and board_connected
                
                sessions.append({
                    'pid': pid,
                    'connection': session.get('connection'),
                    'agent_port': agent_port,
                    'created': session.get('created'),
                    'terminal_pid': terminal_pid,
                    'valid': is_valid,
                    'terminal_running': terminal_running,
                    'agent_running': agent_running,
                    'board_connected': board_connected,
                    'filepath': filepath
                })
            except Exception:
                continue
    
    return sessions

def _cleanup_orphaned_sessions() -> list:
    """
    Remove orphaned session files and return list of cleaned up sessions.
    """
    cleaned = []
    sessions = _list_all_sessions()
    
    for session in sessions:
        if not session['valid']:
            try:
                os.remove(session['filepath'])
                cleaned.append(session)
            except Exception:
                pass
    
    return cleaned

# ============================================================================
# Agent port allocation
# ============================================================================

DEFAULT_AGENT_PORT = 49152
MAX_AGENT_PORT = 49200

def _find_available_agent_port(env_path: str) -> int:
    """
    Find an available agent port.
    
    Rules:
    1. Start from 49152
    2. Skip ports that are registered in .replx AND have a responding agent
    """
    env_data = _read_env_ini(env_path) if env_path and os.path.exists(env_path) else {'connections': {}}
    
    # Collect registered ports
    registered_ports = {}
    for conn_key, conn_data in env_data['connections'].items():
        port = conn_data.get('agent_port')
        if port:
            registered_ports[port] = conn_key
    
    # Find first available port
    for port in range(DEFAULT_AGENT_PORT, MAX_AGENT_PORT):
        if port in registered_ports:
            # Check if agent is actually running on this port
            if AgentClient.is_agent_running(port=port):
                continue  # Port is in use
        # Port is available
        return port
    
    # Fallback to default
    return DEFAULT_AGENT_PORT

# ============================================================================
# Connection resolution (Global option -> Session -> DEFAULT)
# ============================================================================

def _resolve_connection(global_port: str = None, global_target: str = None) -> dict:
    """
    Resolve which connection to use based on priority:
    1. Global option (--port or --target)
    2. Session file
    3. .replx DEFAULT
    
    Returns:
        dict with:
        {
            'connection': 'COM3' or '192.168.1.10',
            'is_serial': True/False,
            'agent_port': 49152,
            'core': 'RP2350',
            'device': 'ticle',
            'password': None or 'mypassword',
            'source': 'global' | 'session' | 'default'
        }
        or None if no connection can be resolved
    """
    env_path = _find_env_file()
    
    # 1. Global option
    if global_port:
        conn_key = global_port.upper()
        result = {
            'connection': conn_key,
            'is_serial': True,
            'source': 'global'
        }
        
        # Try to get existing config
        if env_path:
            config = _get_connection_config(env_path, conn_key)
            if config:
                result['agent_port'] = config.get('agent_port')
                result['core'] = config.get('core')
                result['device'] = config.get('device')
        
        # Assign agent port if not found
        if not result.get('agent_port'):
            result['agent_port'] = _find_available_agent_port(env_path)
        
        return result
    
    if global_target:
        # Parse target (IP:PASSWORD or IP)
        if ':' in global_target:
            parts = global_target.rsplit(':', 1)
            conn_key = parts[0]
            password = parts[1] if len(parts) > 1 else None
        else:
            conn_key = global_target
            password = None
        
        result = {
            'connection': conn_key,
            'is_serial': False,
            'password': password,
            'source': 'global'
        }
        
        # Try to get existing config
        if env_path:
            config = _get_connection_config(env_path, conn_key)
            if config:
                result['agent_port'] = config.get('agent_port')
                result['core'] = config.get('core')
                result['device'] = config.get('device')
                if not password:
                    result['password'] = config.get('password')
        
        # Assign agent port if not found
        if not result.get('agent_port'):
            result['agent_port'] = _find_available_agent_port(env_path)
        
        return result
    
    # 2. Session file
    session = _read_session()
    if session:
        conn_key = session['connection']
        agent_port = session['agent_port']
        
        # Verify agent is running AND board is connected
        agent_running = AgentClient.is_agent_running(port=agent_port)
        board_connected = False
        
        if agent_running:
            try:
                with AgentClient(port=agent_port) as client:
                    status = client.send_command('status', timeout=1.0)
                    board_connected = status.get('connected', False)
            except Exception:
                board_connected = False
        
        if agent_running and board_connected:
            result = {
                'connection': conn_key,
                'is_serial': '.' not in conn_key,  # IP contains dot
                'agent_port': agent_port,
                'source': 'session'
            }
            
            # Get additional config
            if env_path:
                config = _get_connection_config(env_path, conn_key)
                if config:
                    result['core'] = config.get('core')
                    result['device'] = config.get('device')
                    result['password'] = config.get('password')
            
            return result
        else:
            # Agent not running or board disconnected
            # Stop agent if running but board disconnected
            if agent_running and not board_connected:
                try:
                    AgentClient.stop_agent(port=agent_port)
                except Exception:
                    pass
            # Clear invalid session
            _delete_session()
    
    # 3. DEFAULT from .replx
    if env_path:
        default_conn = _get_default_connection(env_path)
        if default_conn:
            config = _get_connection_config(env_path, default_conn)
            if config:
                return {
                    'connection': default_conn,
                    'is_serial': '.' not in default_conn,
                    'agent_port': config.get('agent_port') or _find_available_agent_port(env_path),
                    'core': config.get('core'),
                    'device': config.get('device'),
                    'password': config.get('password'),
                    'source': 'default'
                }
    
    return None

# ============================================================================
# Legacy compatibility functions (to be removed after migration)
# ============================================================================

def _read_env_config(env_path: str) -> dict:
    """Read connection and device info from .replx file."""
    result = {
        'serial_port': None,
        'target': None,
        'core': None,
        'device': None,
        'agent_port': None
    }
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse SERIAL_PORT
        m = re.search(r'^SERIAL_PORT=(.*)$', content, flags=re.MULTILINE)
        if m:
            result['serial_port'] = m.group(1).strip()
        
        # Parse TARGET
        m = re.search(r'^TARGET=(.*)$', content, flags=re.MULTILINE)
        if m:
            result['target'] = m.group(1).strip()
        
        # Parse CORE
        m = re.search(r'^CORE=(.*)$', content, flags=re.MULTILINE)
        if m:
            result['core'] = m.group(1).strip()
        
        # Parse DEVICE
        m = re.search(r'^DEVICE=(.*)$', content, flags=re.MULTILINE)
        if m:
            result['device'] = m.group(1).strip()
        
        # Parse AGENT_PORT
        m = re.search(r'^AGENT_PORT=(.*)$', content, flags=re.MULTILINE)
        if m:
            try:
                result['agent_port'] = int(m.group(1).strip())
            except ValueError:
                pass
        
        return result
    except Exception:
        return result

def _write_env_config(env_path: str, serial_port: Optional[str] = None, target: Optional[str] = None, 
                      core: Optional[str] = None, device: Optional[str] = None, agent_port: Optional[int] = None):
    """
    Write connection and device info to .replx file.
    SERIAL_PORT and TARGET are mutually exclusive.
    
    Args:
        env_path: Path to .replx file
        serial_port: Serial port (e.g., COM16)
        target: WebREPL target (e.g., 192.168.101.101:123456)
        core: Core type (e.g., RP2350)
        device: Device name (e.g., ticle)
        agent_port: Agent UDP port (e.g., 49152)
    """
    if serial_port and target:
        raise ValueError("SERIAL_PORT and TARGET are mutually exclusive")
    
    content = ""
    
    # Connection info (mutually exclusive)
    if serial_port:
        content += f"SERIAL_PORT={serial_port}\n"
    elif target:
        content += f"TARGET={target}\n"
    
    # Device info (always included if provided)
    if core:
        content += f"CORE={core}\n"
    if device:
        content += f"DEVICE={device}\n"
    
    # Agent port (for multi-device support)
    if agent_port:
        content += f"AGENT_PORT={agent_port}\n"
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)

def _tiny_command(cmd:str) -> None:
    """
    Execute a command on the connected device, wrapping it if necessary.
    :param cmd: The command to execute.
    """
    import ast

    try:
        tree = ast.parse(cmd, mode="exec")
        is_expr = (
            len(tree.body) == 1 and
            isinstance(tree.body[0], ast.Expr)
        )
    except SyntaxError:
        is_expr = False

    if is_expr:
        wrapped = (
            f"_r = {cmd}\n"
            "if _r is not None:\n"
            "    print(repr(_r))\n"
        )
    else:
        wrapped = cmd if cmd.endswith("\n") else cmd + "\n"

    # Execute via agent
    _ensure_connected()
    
    try:
        with AgentClient(port=_get_agent_port()) as client:
            result = client.send_command('exec', code=wrapped)
        
        output = result.get('output', '')
        print(output, end="", flush=True)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

def _handle_connection_error(e: Exception, port: str = None, target: str = None):
    """
    Handle connection errors by showing appropriate message and stopping agent.
    
    Args:
        e: The exception that occurred
        port: Serial port if serial connection
        target: WebREPL target if WebREPL connection
    """
    # Build connection info string
    if target:
        # Mask password for WebREPL
        if ':' in target:
            ip, pw = target.rsplit(':', 1)
            masked_pw = pw[:4] + '*' * (len(pw) - 4) if len(pw) > 4 else '****'
            conn_info = f"{ip}:{masked_pw}"
        else:
            conn_info = target
    elif port:
        conn_info = port
    else:
        conn_info = "unknown"
    
    # Stop agent if running (need to get port before _get_agent_port is defined)
    # This function is called on error, try to stop agent on configured port
    try:
        env_path = _find_env_file()
        agent_udp_port = None
        if env_path:
            config = _read_env_config(env_path)
            agent_udp_port = config.get('agent_port')
        if AgentClient.is_agent_running(port=agent_udp_port):
            AgentClient.stop_agent(port=agent_udp_port)
    except:
        pass
    
    OutputHelper.print_panel(
        f"Connection failure on configured device ([bright_blue]{conn_info}[/bright_blue]).\n\n"
        "Please check:\n"
        "  • Device is powered on and connected\n"
        "  • Serial cable is properly attached\n"
        "  • Network connection is available (for WebREPL)\n\n"
        "[dim]Run 'replx --port PORT setup' or 'replx --target IP:PASSWD setup' to reconfigure if needed.[/dim]",
        title="Connection Error",
        border_style="red"
    )

# Global options storage (set by cli callback)
_GLOBAL_OPTIONS = {
    'port': None,
    'target': None,
    'agent_port': None
}

def _set_global_options(port: str = None, target: str = None, agent_port: int = None):
    """Set global options from CLI callback."""
    _GLOBAL_OPTIONS['port'] = port
    _GLOBAL_OPTIONS['target'] = target
    _GLOBAL_OPTIONS['agent_port'] = agent_port

def _get_global_options() -> dict:
    """Get current global options."""
    return _GLOBAL_OPTIONS.copy()

def _ensure_connected_v2(ctx: typer.Context = None) -> dict:
    """
    Ensure agent is running and connected before executing command.
    Uses new multi-device connection resolution.
    
    Priority:
    1. Global options (--port/--target from CLI)
    2. Session file (terminal-specific)
    3. DEFAULT from .replx
    
    Returns:
        dict with connection status from agent
    """
    # Get global options
    global_opts = _get_global_options()
    global_port = global_opts.get('port')
    global_target = global_opts.get('target')
    global_agent_port = global_opts.get('agent_port')
    
    # Resolve connection
    conn = _resolve_connection(global_port, global_target)
    
    if not conn:
        OutputHelper.print_panel(
            "No active connection to device.\n\n"
            "Run [bright_blue]replx --port PORT setup[/bright_blue] first to configure your environment.\n\n"
            "Examples:\n"
            "  [bright_green]replx --port COM3 setup[/bright_green]\n"
            "  [bright_green]replx --port auto setup[/bright_green]  [dim]# Auto-detect port[/dim]\n"
            "  [bright_green]replx --target 192.168.1.100:password setup[/bright_green]",
            title="Setup Required",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Override agent port if explicitly specified
    agent_port = global_agent_port or conn.get('agent_port') or DEFAULT_AGENT_PORT
    
    # Check if agent is running
    if not AgentClient.is_agent_running(port=agent_port):
        # Need to start agent and connect
        OutputHelper.print_panel(
            f"Auto-starting agent for {conn['connection']}...",
            title="Agent",
            border_style="blue"
        )
        
        try:
            AgentClient.start_agent(port=agent_port)
        except Exception as e:
            OutputHelper.print_panel(
                f"Failed to start agent: {str(e)}",
                title="Agent Error",
                border_style="red"
            )
            raise typer.Exit(1)
        
        # Connect
        try:
            port_arg = conn['connection'] if conn['is_serial'] else None
            target_arg = None
            if not conn['is_serial']:
                if conn.get('password'):
                    target_arg = f"{conn['connection']}:{conn['password']}"
                else:
                    target_arg = conn['connection']
            
            with AgentClient(port=agent_port) as client:
                result = client.send_command(
                    'connect', 
                    port=port_arg, 
                    target=target_arg,
                    core=conn.get('core') or "RP2350",
                    device=conn.get('device')
                )
            
            # Update local state
            STATE.core = result.get('core', conn.get('core', ''))
            STATE.device = result.get('device', conn.get('device', 'unknown'))
            STATE.version = result.get('version', '?')
            
            # Update session file
            _write_session(conn['connection'], agent_port)
            
            # Update .replx if this is a new connection from global option
            if conn['source'] == 'global':
                env_path = _find_env_file()
                if not env_path:
                    vscode_dir = _find_or_create_vscode_dir()
                    env_path = os.path.join(vscode_dir, '.replx')
                
                _update_connection_config(
                    env_path,
                    conn['connection'],
                    core=STATE.core,
                    device=STATE.device,
                    agent_port=agent_port,
                    password=conn.get('password'),
                    set_default=False  # Don't change default for regular commands
                )
            
        except Exception as e:
            _handle_connection_error(e, 
                port=conn['connection'] if conn['is_serial'] else None,
                target=conn['connection'] if not conn['is_serial'] else None)
            raise typer.Exit(1)
    
    # Agent is running - get status
    try:
        with AgentClient(port=agent_port) as client:
            status = client.send_command('status')
        
        # Update local state
        STATE.core = status.get('core', STATE.core)
        STATE.device = status.get('device', STATE.device)
        STATE.version = status.get('version', STATE.version)
        
        # Update session file to keep it fresh
        _write_session(conn['connection'], agent_port)
        
        # Update global context for helpers
        set_global_context(STATE.core, STATE.device, STATE.version, STATE.device_root_fs, STATE.device_path, None)
        
        return status
        
    except Exception as e:
        _handle_connection_error(e,
            port=conn['connection'] if conn['is_serial'] else None,
            target=conn['connection'] if not conn['is_serial'] else None)
        raise typer.Exit(1)

def _get_current_agent_port() -> int:
    """Get agent port for current connection (from session or resolved)."""
    session = _read_session()
    if session:
        return session.get('agent_port', DEFAULT_AGENT_PORT)
    
    global_opts = _get_global_options()
    if global_opts.get('agent_port'):
        return global_opts['agent_port']
    
    conn = _resolve_connection(global_opts.get('port'), global_opts.get('target'))
    if conn:
        return conn.get('agent_port', DEFAULT_AGENT_PORT)
    
    return DEFAULT_AGENT_PORT

# Legacy function - redirect to new implementation
def _get_agent_port() -> int | None:
    """
    Get the agent UDP port for current connection.
    Legacy wrapper for compatibility.
    """
    return _get_current_agent_port()

# Legacy function - redirect to new implementation  
def _ensure_connected() -> dict:
    """
    Ensure agent is running (which means connected) before executing command.
    Legacy wrapper - redirects to _ensure_connected_v2.
    """
    return _ensure_connected_v2()

def _get_console(**kwargs):
    """Get a console with width forced for help output.
    
    Accepts all keyword arguments that Typer passes, including stderr,
    force_terminal, force_interactive, soft_wrap, and theme.
    """
    kwargs['width'] = CONSOLE_WIDTH
    kwargs['legacy_windows'] = False
    return Console(**kwargs)

# Replace the get_rich_console at module level if available
try:
    typer.rich_utils._get_rich_console = _get_console
except AttributeError:
    pass

# Also patch the RichCommand to use fixed width
try:
    from typer.core import RichCommand
    _original_rich_command_format_help = RichCommand.format_help
    
    def _format_help_width(self, ctx, formatter):
        old_console = getattr(self, '_rich_console', None)
        try:
            self._rich_console = Console(width=CONSOLE_WIDTH, legacy_windows=False)
            return _original_rich_command_format_help(self, ctx, formatter)
        finally:
            if old_console is not None:
                self._rich_console = old_console
    
    RichCommand.format_help = _format_help_width
except ImportError:
    pass

# Custom error handler for unknown commands
import click
from click.exceptions import UsageError, BadParameter
from rich.panel import Panel

# Override Click's UsageError formatting
_original_usage_error_format_message = UsageError.format_message
_original_usage_error_show = UsageError.show

# Always suppress usage output - we handle it in our custom error handler
# Save original Context.get_usage
_original_context_get_usage = click.Context.get_usage

def _custom_context_get_usage(self):
    """Always suppress usage output - our custom error handler includes it."""
    return ""

# Monkey-patch Click's Context
click.Context.get_usage = _custom_context_get_usage

def _build_command_help(ctx) -> str:
    """Build command help text from context (without Examples)."""
    if not ctx or not ctx.command:
        return None
    
    cmd = ctx.command
    cmd_name = ctx.info_name
    
    lines = []
    
    # Description
    if cmd.help:
        lines.append(cmd.help.split('\n')[0])  # First line only
        lines.append("")
    
    # Usage
    params_str = ""
    options = []
    arguments = []
    
    for param in cmd.params:
        if isinstance(param, click.Option):
            if not param.hidden:
                options.append(param)
        elif isinstance(param, click.Argument):
            arguments.append(param)
    
    if options:
        params_str += "[[cyan]OPTIONS[/cyan]] "
    for arg in arguments:
        arg_name = arg.name.upper()
        if arg.required:
            params_str += f"[yellow]{arg_name}[/yellow] "
        else:
            params_str += f"[yellow][{arg_name}][/yellow] "
    
    lines.append(f"[bold cyan]Usage:[/bold cyan]")
    lines.append(f"  replx {cmd_name} {params_str.strip()}")
    lines.append("")
    
    # Options
    if options:
        lines.append("[bold cyan]Options:[/bold cyan]")
        for opt in options:
            opt_str = ", ".join(opt.opts)
            if opt.metavar:
                opt_str += f" [green]{opt.metavar}[/green]"
            elif opt.type and opt.type.name.upper() not in ('BOOL', 'BOOLEAN'):
                opt_str += f" [green]{opt.type.name.upper()}[/green]"
            
            help_text = opt.help or ""
            # Truncate long help
            if len(help_text) > 40:
                help_text = help_text[:37] + "..."
            
            lines.append(f"  {opt_str:<25} {help_text}")
        lines.append("")
    
    # Arguments
    if arguments:
        lines.append("[bold cyan]Arguments:[/bold cyan]")
        for arg in arguments:
            req = "[red][required][/red]" if arg.required else "[dim][optional][/dim]"
            lines.append(f"  [yellow]{arg.name}[/yellow]  {req}")
    
    return "\n".join(lines)

def _custom_usage_error_show(self, file=None):
    """Custom error display in a single box."""
    import sys
    
    console = Console(width=CONSOLE_WIDTH, file=sys.stderr)
    
    error_msg = _original_usage_error_format_message(self)
    error_lines = []
    
    # Check if this is a command-specific error (has context with command info)
    cmd_name = None
    if self.ctx and self.ctx.info_name and self.ctx.info_name != 'replx':
        cmd_name = self.ctx.info_name
    
    # Check error type - option/argument errors for valid commands
    is_option_error = any(x in error_msg.lower() for x in ['no such option', 'missing option', 'missing argument', 'invalid value', 'requires an argument', 'got unexpected'])
    
    if cmd_name and is_option_error:
        # Show command-specific help (without Examples)
        help_text = _build_command_help(self.ctx)
        if help_text:
            error_lines.append(help_text)
            error_lines.append("")
            error_lines.append(f"[red]{error_msg}[/red]")
        else:
            # Fallback: show basic usage
            error_lines.append(f"[bold cyan]Usage:[/bold cyan] replx {cmd_name} [OPTIONS] [ARGS]...")
            error_lines.append("")
            error_lines.append(f"[red]{error_msg}[/red]")
    else:
        # Unknown command or general error - add Usage line
        error_lines.append("[bold cyan]Usage:[/bold cyan] replx [OPTIONS] COMMAND [ARGS]...")
        error_lines.append("")
        error_lines.append(f"[red]{error_msg}[/red]")
    
    console.print(Panel(
        "\n".join(error_lines),
        title="Error",
        border_style="red",
        box=get_panel_box(),
        width=CONSOLE_WIDTH
    ))

def _handle_usage_error(e):
    """Handle UsageError exceptions with custom formatting."""
    import sys
    
    console = Console(width=CONSOLE_WIDTH, file=sys.stderr)
    
    error_msg = str(e.format_message()) if hasattr(e, 'format_message') else str(e)
    error_lines = []
    
    # Check if this is a command-specific error (has context with command info)
    cmd_name = None
    if e.ctx and e.ctx.info_name and e.ctx.info_name != 'replx':
        cmd_name = e.ctx.info_name
    
    # Check error type - option/argument errors for valid commands
    is_option_error = any(x in error_msg.lower() for x in ['no such option', 'missing option', 'missing argument', 'invalid value', 'requires an argument', 'got unexpected'])
    
    if cmd_name and is_option_error:
        # Show command-specific help (without Examples)
        help_text = _build_command_help(e.ctx)
        if help_text:
            error_lines.append(help_text)
            error_lines.append("")
            error_lines.append(f"[red]{error_msg}[/red]")
        else:
            # Fallback: show basic usage
            error_lines.append(f"[bold cyan]Usage:[/bold cyan] replx {cmd_name} [OPTIONS] [ARGS]...")
            error_lines.append("")
            error_lines.append(f"[red]{error_msg}[/red]")
    else:
        # Unknown command or general error - add Usage line
        error_lines.append("[bold cyan]Usage:[/bold cyan] replx [OPTIONS] COMMAND [ARGS]...")
        error_lines.append("")
        error_lines.append(f"[red]{error_msg}[/red]")
    
    console.print(Panel(
        "\n".join(error_lines),
        title="Error",
        border_style="red",
        box=get_panel_box(),
        width=CONSOLE_WIDTH
    ))

UsageError.show = _custom_usage_error_show

app = typer.Typer(
    help="MicroPython REPL tool for device management",
    no_args_is_help=False,  # We handle this manually
    add_completion=False,
    rich_markup_mode="rich",  # Enable rich formatting for help
    context_settings={
        "max_content_width": CONSOLE_WIDTH
    },
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False  # Disable pretty exceptions
)

# Session subcommand app
session_app = typer.Typer(
    help="Manage device sessions",
    no_args_is_help=False,
    add_completion=False,
    rich_markup_mode="rich",
    invoke_without_command=True,
)
app.add_typer(session_app, name="session")

def _print_main_help():
    """Print custom main help in a single box."""
    from rich.panel import Panel
    console = Console(width=CONSOLE_WIDTH)
    
    # Build help text
    lines = []
    lines.append("MicroPython REPL tool for device management.")
    lines.append("")
    lines.append("[bold cyan]Usage:[/bold cyan]")
    lines.append("  replx [yellow][OPTIONS][/yellow] [yellow]COMMAND[/yellow] [[cyan]ARGS[/cyan]]...")
    lines.append("")
    lines.append("[bold cyan]Global Options:[/bold cyan]")
    lines.append("  [yellow]--port, -p[/yellow] [cyan]PORT[/cyan]      Serial port (e.g., COM3)")
    lines.append("  [yellow]--target, -t[/yellow] [cyan]PAIR[/cyan]    WebREPL target (IP:PASSWORD)")
    lines.append("  [yellow]--agent-port[/yellow] [cyan]PORT[/cyan]    Agent UDP port (auto-assigned)")
    lines.append("")
    lines.append("[bold cyan]Commands:[/bold cyan]")
    
    # Command descriptions (organized by category)
    commands = [
        # Quick commands (with aliases)
        ("version", "Show replx version (-v)"),
        ("exec", "Execute MicroPython command (-c)"),
        # Setup & Connection
        ("setup", "Initialize environment and connect to device"),
        ("free", "Release port by stopping the agent"),
        ("session", "Manage sessions (list, attach, cleanup)"),
        ("scan", "Scan and list connected MicroPython boards"),
        ("repl", "Enter REPL (Read-Eval-Print Loop) mode"),
        ("shell", "Enter interactive shell for device control"),
        ("reset", "Reset the connected device"),
        # File operations
        ("ls", "List directory contents on device"),
        ("cat", "Display file content from device"),
        ("get", "Download file(s) or directory from device"),
        ("put", "Upload file(s) or directory to device"),
        ("cp", "Copy file or directory on device"),
        ("mv", "Move/rename file(s) or directory on device"),
        ("rm", "Remove files or directories from device"),
        ("mkdir", "Create directories on device"),
        ("touch", "Create empty files on device"),
        # Device info
        ("info", "Show device memory and storage status"),
        # Device management
        ("run", "Run a script on device"),
        ("format", "Format device filesystem"),
        ("init", "Initialize device (format + install libraries)"),
        # Library management
        ("install", "Install libraries/files onto device"),
        ("update", "Update local library store"),
        ("search", "Search for libraries in remote registry"),
    ]
    
    for cmd, desc in commands:
        lines.append(f"  [green]{cmd:<12}[/green] {desc}")
    
    lines.append("")
    lines.append("[dim]Use 'replx COMMAND --help' for more information on a command.[/dim]")
    
    console.print(Panel(
        "\n".join(lines),
        title="replx",
        border_style="bright_blue",
        box=get_panel_box(),
        width=CONSOLE_WIDTH
    ))

@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    global_port: Optional[str] = typer.Option(
        None,
        "--port", "-p",
        help="Serial port to use (e.g., COM3)",
        is_eager=True
    ),
    global_target: Optional[str] = typer.Option(
        None,
        "--target", "-t", 
        help="WebREPL target (IP:PASSWORD)",
        is_eager=True
    ),
    global_agent_port: Optional[int] = typer.Option(
        None,
        "--agent-port",
        help="Agent UDP port (auto-assigned if not specified)",
        is_eager=True
    ),
    show_help: bool = typer.Option(
        False,
        "--help",
        is_eager=True,
        expose_value=True,
        help="Show this message and exit."
    )
):
    """
    MicroPython REPL tool for device management.
    
    Use 'replx setup --port PORT' to connect, then run commands.
    """
    
    # Validate mutual exclusivity
    if global_port and global_target:
        OutputHelper.print_panel(
            "[red]Error:[/red] --port and --target cannot be used together.",
            title="Invalid Options",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Store global options in module-level storage for access by all commands
    _set_global_options(global_port, global_target, global_agent_port)
    
    # Also store in context for subcommands that receive ctx
    ctx.ensure_object(dict)
    ctx.obj['global_port'] = global_port
    ctx.obj['global_target'] = global_target
    ctx.obj['global_agent_port'] = global_agent_port
    
    # Handle help flag first
    if show_help:
        _print_main_help()
        raise typer.Exit()
    
    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        _print_main_help()
        raise typer.Exit()

# =============================================================================
# Quick Commands (with short aliases)
# =============================================================================

@app.command(name="version")
def version_cmd(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Show replx version information.
    
    Alias: replx -v
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Show replx version information.

[bold cyan]Usage:[/bold cyan]
  replx version
  replx -v                [dim]# Short alias[/dim]

[bold cyan]Examples:[/bold cyan]
  replx version           [dim]# Show version[/dim]
  replx -v                [dim]# Same as above[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    OutputHelper.print_panel(
        f"replx [green]{__version__}[/green]",
        title="Version",
        border_style="cyan"
    )

@app.command(name="exec")
def exec_cmd(
    command: str = typer.Argument("", help="MicroPython command to execute"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Execute a single MicroPython command on the device.
    
    Alias: replx -c "command"
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Execute a single MicroPython command on the device.

[bold cyan]Usage:[/bold cyan]
  replx exec [yellow]COMMAND[/yellow]
  replx -c [yellow]COMMAND[/yellow]         [dim]# Short alias[/dim]

[bold cyan]Arguments:[/bold cyan]
  [yellow]command[/yellow]     MicroPython command to execute [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx exec "print('hello')"           [dim]# Print message[/dim]
  replx -c "print('hello')"             [dim]# Same as above[/dim]
  replx exec "import os; os.listdir()"  [dim]# List files[/dim]
  replx -c "1+2"                        [dim]# Evaluate expression[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    if not command:
        OutputHelper.print_panel(
            "Missing required argument.\n\n"
            "[bold cyan]Usage:[/bold cyan] replx exec [yellow]COMMAND[/yellow]\n"
            "       replx -c [yellow]COMMAND[/yellow]",
            title="Exec Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    _tiny_command(command)

# =============================================================================
# Setup & Connection Commands
# =============================================================================

@app.command()
def setup(
    keep: bool = typer.Option(False, "--keep", "-k", help="Keep current default, don't change to this connection"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Initialize replx environment and connect to device.
    Sets up workspace with configuration, type stubs, and VS Code settings.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Initialize replx environment and connect to device.

[bold cyan]Usage:[/bold cyan]
  replx [yellow]--port PORT[/yellow] | [yellow]--target IP:PASSWORD[/yellow] setup [yellow][--keep][/yellow]

[bold cyan]Global Options:[/bold cyan]
  [yellow]--port, -p PORT[/yellow]           Serial port (e.g., COM3) or 'auto' for auto-detect
  [yellow]--target, -t IP:PASSWORD[/yellow]  WebREPL target
  [yellow]--agent-port, -a PORT[/yellow]     Agent UDP port (auto-allocated if not specified)

[bold cyan]Command Options:[/bold cyan]
  [yellow]--keep, -k[/yellow]                Keep current default connection

[bold cyan]Examples:[/bold cyan]
  replx --port COM3 setup                 [dim]# Setup COM3 as default[/dim]
  replx --port auto setup                 [dim]# Auto-detect and set as default[/dim]
  replx --target 192.168.1.100:pwd setup  [dim]# Setup WebREPL as default[/dim]
  replx --port COM8 setup --keep          [dim]# Add COM8 without changing default[/dim]
  replx --port COM3 --agent-port 49153 setup  [dim]# Specify agent port[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    # Get global options
    global_opts = _get_global_options()
    port = global_opts.get('port')
    target = global_opts.get('target')
    agent_port = global_opts.get('agent_port')
    
    # If no options provided, try to connect using .replx or show current status
    if not port and not target:
        env_path = _find_env_file()
        
        # Try to resolve existing connection
        conn = _resolve_connection()
        
        if conn and conn.get('agent_port'):
            check_port = conn['agent_port']
            # Check if already connected
            if AgentClient.is_agent_running(port=check_port):
                try:
                    with AgentClient(port=check_port) as client:
                        status = client.send_command('status', timeout=1.0)
                    
                    if status.get('connected'):
                        # Show current connection status
                        device = status.get('device', 'unknown')
                        core = status.get('core', 'unknown')
                        version = status.get('version', '?')
                        port_name = status.get('port', 'unknown')
                        conn_type = status.get('connection_type', 'serial')
                        
                        workspace = os.path.dirname(os.path.dirname(env_path)) if env_path else os.getcwd()
                        
                        # Get default connection
                        default_conn = _get_default_connection(env_path) if env_path else None
                        
                        content = f"Device: [bright_yellow]{device}[/bright_yellow] on [bright_green]{core}[/bright_green]\n"
                        content += f"Connection: [bright_blue]{conn_type}[/bright_blue] ({port_name})\n"
                        content += f"Agent Port: [bright_cyan]{check_port}[/bright_cyan]\n"
                        if default_conn:
                            content += f"Default: [dim]{default_conn}[/dim]\n"
                        content += f"Version: [yellow]{version}[/yellow]\n"
                        content += f"Workspace: [dim]{workspace}[/dim]"
                        
                        OutputHelper.print_panel(
                            content,
                            title="Current Connection",
                            border_style="green"
                        )
                        raise typer.Exit()
                except typer.Exit:
                    raise
                except Exception:
                    pass
        
        # Not connected - check if .replx has DEFAULT
        if env_path:
            default_conn = _get_default_connection(env_path)
            if default_conn:
                config = _get_connection_config(env_path, default_conn)
                if config:
                    # Use default connection
                    is_serial = '.' not in default_conn
                    if is_serial:
                        port = default_conn
                    else:
                        if config.get('password'):
                            target = f"{default_conn}:{config['password']}"
                        else:
                            target = default_conn
                    agent_port = config.get('agent_port')
                    # Continue to normal connection flow below
                else:
                    # DEFAULT exists but no config
                    OutputHelper.print_panel(
                        "Default connection configured but no settings found.\n\n"
                        "Examples:\n"
                        "  [bright_green]replx --port COM3 setup[/bright_green]\n"
                        "  [bright_green]replx --port auto setup[/bright_green]  [dim]# Auto-detect port[/dim]\n"
                        "  [bright_green]replx --target 192.168.1.100:password setup[/bright_green]",
                        title="Setup Required",
                        border_style="yellow"
                    )
                    raise typer.Exit(1)
            else:
                # .replx exists but no DEFAULT
                OutputHelper.print_panel(
                    "Configuration file found but no default connection.\n\n"
                    "Examples:\n"
                    "  [bright_green]replx --port COM3 setup[/bright_green]\n"
                    "  [bright_green]replx --port auto setup[/bright_green]  [dim]# Auto-detect port[/dim]\n"
                    "  [bright_green]replx --target 192.168.1.100:password setup[/bright_green]",
                    title="Setup Required",
                    border_style="yellow"
                )
                raise typer.Exit(1)
        else:
            # No .replx file - show help
            OutputHelper.print_panel(
                "Either [bright_blue]--port[/bright_blue] or [bright_blue]--target[/bright_blue] is required.\n\n"
                "Examples:\n"
                "  [bright_green]replx --port COM3 setup[/bright_green]\n"
                "  [bright_green]replx --port auto setup[/bright_green]  [dim]# Auto-detect port[/dim]\n"
                "  [bright_green]replx --target 192.168.1.100:password setup[/bright_green]",
                title="Setup Required",
                border_style="yellow"
            )
            raise typer.Exit(1)
    
    if port and target:
        OutputHelper.print_panel(
            "Cannot use both [bright_blue]--port[/bright_blue] and [bright_blue]--target[/bright_blue] simultaneously.",
            title="Conflicting Options",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Handle auto-detect port
    if port and port.lower() == "auto":
        OutputHelper.print_panel(
            "Scanning for MicroPython devices...",
            title="Auto-detect",
            border_style="blue"
        )
        detected_port = _auto_detect_port()
        if not detected_port:
            OutputHelper.print_panel(
                "No MicroPython device found.\n"
                "Make sure the device is connected and try again,\n"
                "or specify the port manually with [bright_blue]--port PORT[/bright_blue].",
                title="No Device Found",
                border_style="red"
            )
            raise typer.Exit(1)
        port = detected_port
        OutputHelper.print_panel(
            f"Found MicroPython device on [bright_green]{port}[/bright_green]",
            title="Auto-detect",
            border_style="green"
        )
    
    # Validate target format
    connection_type = "webrepl" if target else "serial"
    if target and ':' not in target:
        OutputHelper.print_panel(
            "Invalid WebREPL target format. Expected [bright_blue]IP:PASSWORD[/bright_blue]",
            title="Invalid Target",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Auto-allocate agent port if not specified
    env_path = _find_env_file()
    if agent_port is None:
        # Check if this connection already has an assigned port
        conn_key = port.upper() if port else (target.rsplit(':', 1)[0] if target else None)
        if env_path and conn_key:
            existing_config = _get_connection_config(env_path, conn_key)
            if existing_config and existing_config.get('agent_port'):
                agent_port = existing_config['agent_port']
        
        # If still None, find available port
        if agent_port is None:
            agent_port = _find_available_agent_port(env_path)
    
    # Check if agent is already running with same configuration (on same agent_port)
    if AgentClient.is_agent_running(port=agent_port):
        try:
            with AgentClient(port=agent_port) as client:
                status = client.send_command('status', timeout=1.0)
            
            # First check: is the board actually connected?
            if not status.get('connected'):
                # Agent running but board disconnected - stop agent and reconnect
                try:
                    AgentClient.stop_agent(port=agent_port)
                    time.sleep(0.5)
                except Exception:
                    pass
                # Continue to normal connection flow below
            elif status.get('connected'):
                current_port = status.get('port', '')
                current_type = status.get('connection_type', 'serial')
                
                # Compare with requested configuration
                same_config = False
                if connection_type == "serial" and current_type == "serial":
                    # Compare port names (normalize case on Windows)
                    if IS_WINDOWS:
                        same_config = current_port.upper() == port.upper()
                    else:
                        same_config = current_port == port
                elif connection_type == "webrepl" and current_type == "webrepl":
                    # Compare target (IP:PASSWORD)
                    same_config = current_port == target
                
                if same_config:
                    # Same configuration - just show status and exit
                    device = status.get('device', 'unknown')
                    core = status.get('core', 'unknown')
                    version = status.get('version', '?')
                    effective_agent_port = agent_port or AgentClient.DEFAULT_AGENT_PORT
                    
                    env_path = _find_env_file()
                    workspace = os.path.dirname(os.path.dirname(env_path)) if env_path else os.getcwd()
                    
                    content = f"Device: [bright_yellow]{device}[/bright_yellow] on [bright_green]{core}[/bright_green]\n"
                    content += f"Connection: [bright_blue]{current_type}[/bright_blue] ({current_port})\n"
                    content += f"Agent Port: [bright_cyan]{effective_agent_port}[/bright_cyan]\n"
                    content += f"Version: [yellow]{version}[/yellow]\n"
                    content += f"Workspace: [dim]{workspace}[/dim]\n\n"
                    content += "[dim]Already connected with same configuration.[/dim]"
                    
                    OutputHelper.print_panel(
                        content,
                        title="Current Connection",
                        border_style="green"
                    )
                    raise typer.Exit()
        except typer.Exit:
            raise
        except Exception:
            # Agent not responding properly - stop and reconnect
            try:
                AgentClient.stop_agent(port=agent_port)
                time.sleep(0.5)
            except Exception:
                pass
    
    # Step 1: Stop existing agent on same port if running
    if AgentClient.is_agent_running(port=agent_port):
        try:
            AgentClient.stop_agent(port=agent_port)
            time.sleep(0.5)
        except Exception:
            pass
    
    # Step 2: Start agent with specified port
    try:
        AgentClient.start_agent(port=agent_port)
    except Exception as e:
        OutputHelper.print_panel(
            f"Failed to start agent: {str(e)}",
            title="Agent Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Step 3: Connect via agent
    try:
        with AgentClient(port=agent_port) as client:
            result = client.send_command('connect', port=port, target=target)
        
        STATE.core = result['core']
        STATE.device = result['device']
        STATE.version = result['version']
    except Exception as e:
        try:
            AgentClient.stop_agent()
        except:
            pass
        
        # Determine connection info for error message
        if port:
            conn_info = port
        elif target:
            conn_info = target
        else:
            conn_info = "unknown"

        OutputHelper.print_panel(
            f"Connection failure on configured device ([bright_blue]{conn_info}[/bright_blue]).\n\n"
            "Please check:\n"
            "  • Device is powered on and connected\n"
            "  • Serial cable is properly attached\n"
            "  • Network connection is available (for WebREPL)\n\n"
            "[dim]Run 'replx setup --port PORT' or 'replx setup --target IP:PASSWD' to reconfigure if needed.[/dim]",
            title="Connection Error",
            border_style="red"
        )
        raise typer.Exit(1)

    # Find or create .vscode directory
    vscode_dir = _find_or_create_vscode_dir()
    env_path = os.path.join(vscode_dir, ".replx")
    
    # Determine connection key for INI storage
    if connection_type == "serial":
        conn_key = port.upper()
        password = None
    else:
        # For WebREPL, extract IP and password
        if ':' in target:
            parts = target.rsplit(':', 1)
            conn_key = parts[0]  # IP address
            password = parts[1]
        else:
            conn_key = target
            password = None
    
    # Determine if we should set this as default
    # --keep option prevents changing the default
    set_as_default = not keep
    
    # Update .replx file using INI format
    _update_connection_config(
        env_path,
        conn_key,
        core=STATE.core,
        device=STATE.device,
        agent_port=agent_port,
        password=password,
        set_default=set_as_default
    )
    
    # Update session file for this terminal
    _write_session(conn_key, agent_port)
    
    # Create VS Code configuration files
    task_file = os.path.join(vscode_dir, "tasks.json")
    settings_file = os.path.join(vscode_dir, "settings.json")
    launch_file = os.path.join(vscode_dir, "launch.json")
    
    task_file_contents = """{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run micropython with replx",
            "type": "shell",
            "command": "replx",
            "args": ["${file}"],
            "problemMatcher": [],
            "group": { "kind": "build", "isDefault": true }
        }
    ]
}
"""
    
    extra_paths = ["./.vscode"]
    if STATE.device:
        extra_paths.append(f"./.vscode/{STATE.device}")
    
    settings_dict = {
        "files.exclude": {
            "**/.vscode": True
        },
        "python.languageServer": "Pylance",
        "python.analysis.diagnosticSeverityOverrides": {
            "reportMissingModuleSource": "none"
        },
        "python.analysis.extraPaths": extra_paths
    }
    settings_file_contents = json.dumps(settings_dict, indent=4) + "\n"
    
    launch_file_contents = """{
    "version": "0.2.0",
    "configurations": [
      {
        "name": "Python: Current file debug",
        "type": "debugpy",
        "request": "launch",
        "program": "${file}",
        "console": "integratedTerminal"
      }
    ]
}
"""
    
    with open(task_file, "w", encoding="utf-8") as f:
        f.write(task_file_contents)
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write(settings_file_contents)
    with open(launch_file, "w", encoding="utf-8") as f:
        f.write(launch_file_contents)
    
    # Link typehints
    linked = 0
    if STATE.core:
        core_typehints = os.path.join(StoreManager.pkg_root(), "core", STATE.core, "typehints")
        linked += EnvironmentManager.link_typehints_into_vscode(core_typehints, vscode_dir)
    if STATE.device:
        device_typehints = os.path.join(StoreManager.pkg_root(), "device", STATE.device, "typehints")
        linked += EnvironmentManager.link_typehints_into_vscode(device_typehints, vscode_dir, subdir=STATE.device)
    
    # Build display connection string
    if connection_type == "serial":
        display_conn = port
    else:
        ip_address = target.rsplit(':', 1)[0]
        pw = target.rsplit(':', 1)[1] if ':' in target else ''
        masked_pw = pw[:4] + '*' * (len(pw) - 4) if len(pw) > 4 else '****'
        display_conn = f"{ip_address}:{masked_pw}"
    
    # Show workspace path relative to home
    workspace = os.path.dirname(vscode_dir)
    effective_agent_port = agent_port or DEFAULT_AGENT_PORT
    
    # Get current default
    current_default = _get_default_connection(env_path)
    
    content = f"Device: [bright_yellow]{STATE.device}[/bright_yellow] on [bright_green]{STATE.core}[/bright_green]\n"
    content += f"Connection: [bright_blue]{connection_type}[/bright_blue] ({display_conn})\n"
    content += f"Agent Port: [bright_cyan]{effective_agent_port}[/bright_cyan]\n"
    if current_default:
        if current_default == conn_key:
            content += f"Default: [bright_green]{current_default}[/bright_green] [dim](this connection)[/dim]\n"
        else:
            content += f"Default: [dim]{current_default}[/dim]\n"
    content += f"Version: [yellow]{STATE.version}[/yellow]\n"
    content += f"Workspace: [dim]{workspace}[/dim]"
    
    OutputHelper.print_panel(
        content,
        title="Setup Complete",
        border_style="green"
    )

@app.command(hidden=True)
def env(
    keep: bool = typer.Option(False, "--keep", "-k", help="Keep current default, don't change to this connection"),
):
    """
    Deprecated alias for 'setup'. Use 'replx setup' instead.
    """
    # Print deprecation warning
    OutputHelper.print_panel(
        "[yellow]Warning:[/yellow] The 'env' command is deprecated and will be removed in a future release.\n"
        "Please use [bright_green]'replx setup'[/bright_green] instead.",
        title="Deprecation Notice",
        border_style="yellow"
    )
    
    # Call the setup function with the same arguments
    setup(keep=keep)

@app.command()
def free(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Free the serial port by stopping the agent.
    
    Releases the port for other applications (e.g., external REPL, firmware update).
    The next replx command will automatically reconnect.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Free the serial port by stopping the agent.

[bold cyan]Usage:[/bold cyan]
  replx free

[bold cyan]Description:[/bold cyan]
  Stops the background agent and releases the serial port.
  This allows other applications to access the device.
  
  The next replx command will automatically reconnect.

[bold cyan]Examples:[/bold cyan]
  replx free               [dim]# Release the port[/dim]
  mpremote connect         [dim]# Use port with another tool[/dim]
  replx ls                 [dim]# Auto-reconnect on next command[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    agent_port = _get_agent_port()
    
    if not AgentClient.is_agent_running(port=agent_port):
        OutputHelper.print_panel(
            "Agent is not running. Port is already free.",
            title="Free",
            border_style="dim"
        )
        raise typer.Exit()
    
    try:
        # Get device info from agent before stopping
        device_name = "unknown"
        port_name = "unknown"
        
        try:
            with AgentClient(port=agent_port) as client:
                status = client.send_command('status', timeout=3.0)
            device_name = status.get('device', 'unknown')
            port_name = status.get('port', 'unknown')
        except Exception as e:
            # Agent may not respond, continue with stop
            pass
        
        # Stop agent (which also frees the port)
        AgentClient.stop_agent(port=agent_port)
        
        # Delete session file for this terminal
        _delete_session()
        
        OutputHelper.print_panel(
            f"Released [bright_green]{port_name}[/bright_green] "
            f"([bright_yellow]{device_name}[/bright_yellow])\n"
            "Port is now free for other use.\n"
            "[dim]Run any replx command to reconnect.[/dim]",
            title="Port Released",
            border_style="blue"
        )
    except Exception as e:
        OutputHelper.print_panel(
            f"Failed to free port: {str(e)}",
            title="Free Error",
            border_style="red"
        )
        raise typer.Exit(1)

# ============================================================================
# Session commands (replx session)
# ============================================================================

def _get_session_list_data():
    """
    Get session list data for display.
    Returns list of dicts with session info including index number.
    
    A session is considered 'active' only when:
    1. Agent process is running on the port
    2. Agent has an active connection to the board (connected=True)
    
    This prevents showing disconnected boards as active.
    """
    env_path = _find_env_file()
    if not env_path:
        return None, None, "no_workspace"
    
    env_data = _read_env_ini(env_path)
    default_conn = env_data.get('default')
    connections_dict = env_data.get('connections', {})
    
    if not connections_dict:
        return None, None, "no_connections"
    
    # Get current terminal's session
    current_session = _read_session()
    current_conn = current_session.get('connection', '') if current_session else ''
    
    sessions = []
    idx = 1
    for conn_key, conn_data in connections_dict.items():
        agent_port = conn_data.get('agent_port', DEFAULT_AGENT_PORT)
        is_default = conn_key == default_conn
        is_current = conn_key.upper() == current_conn.upper() if current_conn else False
        
        device = conn_data.get('device', '-') or '-'
        core = conn_data.get('core', '-') or '-'
        
        # Check if agent is running AND board is actually connected
        is_active = False
        board_connected = False
        version = None
        
        if AgentClient.is_agent_running(port=agent_port):
            try:
                with AgentClient(port=agent_port) as client:
                    status = client.send_command('status', timeout=1.0)
                    # Agent is active only if board is connected
                    board_connected = status.get('connected', False)
                    is_active = board_connected
                    if is_active:
                        version = status.get('version', '?')
                        # Update device/core from live status if available
                        if status.get('device'):
                            device = status.get('device')
                        if status.get('core'):
                            core = status.get('core')
            except Exception:
                is_active = False
        
        sessions.append({
            'index': idx,
            'key': conn_key,
            'device': device,
            'core': core,
            'agent_port': agent_port,
            'is_active': is_active,
            'is_default': is_default,
            'is_current': is_current,
            'version': version,
            'board_connected': board_connected,
        })
        idx += 1
    
    return sessions, default_conn, None

def _print_session_list(sessions, show_attach_hint=True):
    """Print formatted session list."""
    from rich.panel import Panel
    
    content_lines = []
    
    for s in sessions:
        # Build status indicators
        prefix = "  "
        if s['is_default'] and s['is_active']:
            prefix = "[green]★[/green] "
        elif s['is_default']:
            prefix = "[yellow]★[/yellow] "
        elif s['is_active']:
            prefix = "[green]●[/green] "
        else:
            prefix = "[dim]○[/dim] "
        
        # Connection name styling
        if s['is_active']:
            conn_display = f"[bright_green]{s['key']}[/bright_green]"
        else:
            conn_display = f"[dim]{s['key']}[/dim]"
        
        # Current terminal indicator
        current_marker = ""
        if s['is_current']:
            current_marker = " [cyan](this terminal)[/cyan]"
        
        # Status text
        if s['is_active']:
            status_text = "[green]active[/green]"
        else:
            status_text = "[dim]inactive[/dim]"
        
        # Device info
        device_info = f"{s['device']} on {s['core']}"
        
        content_lines.append(
            f"[bright_cyan][{s['index']}][/bright_cyan] {prefix}{conn_display} - {device_info} {status_text}{current_marker}"
        )
    
    if show_attach_hint:
        content_lines.append("")
        content_lines.append("[dim]★ = default, ● = active, ○ = inactive[/dim]")
    
    OutputHelper.print_panel(
        "\n".join(content_lines),
        title="Sessions",
        border_style="cyan"
    )

def _do_attach(conn_key: str, conn_data: dict, is_current: bool) -> bool:
    """
    Attach to a session. Returns True on success.
    Verifies both agent running AND board connected before attaching.
    """
    if is_current:
        OutputHelper.print_panel(
            f"Already attached to [bright_green]{conn_key}[/bright_green]",
            title="ℹ Info",
            border_style="blue"
        )
        return True
    
    agent_port = conn_data.get('agent_port', DEFAULT_AGENT_PORT)
    
    # Check if agent is running
    if not AgentClient.is_agent_running(port=agent_port):
        OutputHelper.print_panel(
            f"Session [bright_yellow]{conn_key}[/bright_yellow] is not active.\n"
            f"Run [bright_green]replx --port {conn_key} setup[/bright_green] to start it.",
            title="Session Not Active",
            border_style="yellow"
        )
        return False
    
    # Get status from agent and verify board is connected
    try:
        with AgentClient(port=agent_port) as client:
            status = client.send_command('status', timeout=2.0)
        
        # Check if board is actually connected
        if not status.get('connected', False):
            OutputHelper.print_panel(
                f"Session [bright_yellow]{conn_key}[/bright_yellow] has no board connected.\n"
                f"The device may have been disconnected.\n"
                f"Run [bright_green]replx --port {conn_key} setup[/bright_green] to reconnect.",
                title="Board Disconnected",
                border_style="yellow"
            )
            return False
        
        device = status.get('device', conn_data.get('device', 'unknown'))
        core = status.get('core', conn_data.get('core', 'unknown'))
        version = status.get('version', '?')
        
        # Update session file
        _write_session(conn_key, agent_port)
        
        # Update local state
        STATE.device = device
        STATE.core = core
        STATE.version = version
        
        OutputHelper.print_panel(
            f"Attached to [bright_green]{conn_key}[/bright_green]\n"
            f"Device: [bright_yellow]{device}[/bright_yellow] on [bright_green]{core}[/bright_green]\n"
            f"Version: [yellow]{version}[/yellow]",
            title="✓ Attached",
            border_style="green"
        )
        return True
    except Exception as e:
        OutputHelper.print_panel(
            f"Failed to attach to {conn_key}: {str(e)}",
            title="Attach Error",
            border_style="red"
        )
        return False

@session_app.callback(invoke_without_command=True)
def session_main(
    ctx: typer.Context,
    target: Optional[str] = typer.Argument(None, help="Session number or connection name to attach"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Manage device sessions interactively.
    
    Without arguments: shows session list and prompts for selection.
    With argument: directly attaches to the specified session.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Manage device sessions.

[bold cyan]Usage:[/bold cyan]
  replx session [yellow][TARGET][/yellow]
  replx session cleanup
  replx session c

[bold cyan]Arguments:[/bold cyan]
  [yellow]TARGET[/yellow]  Session number (1, 2, ...) or connection name (COM3, 192.168.1.10)
          If omitted, shows interactive session list.

[bold cyan]Subcommands:[/bold cyan]
  [green]cleanup, c[/green]  Clean up orphaned session files

[bold cyan]Examples:[/bold cyan]
  replx session          [dim]# Interactive: list + select[/dim]
  replx session 1        [dim]# Attach to session #1[/dim]
  replx session COM3     [dim]# Attach to COM3[/dim]
  replx session cleanup  [dim]# Clean up orphaned sessions[/dim]
  replx session c        [dim]# Short form of cleanup[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    # If subcommand was invoked, don't run this
    if ctx.invoked_subcommand is not None:
        return
    
    # Get session data
    sessions, default_conn, error = _get_session_list_data()
    
    if error == "no_workspace":
        OutputHelper.print_panel(
            "No workspace found.\n"
            "Run [bright_green]replx --port PORT setup[/bright_green] to configure.",
            title="No Sessions",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    if error == "no_connections":
        OutputHelper.print_panel(
            "No sessions registered.\n"
            "Run [bright_green]replx --port PORT setup[/bright_green] to add a session.",
            title="No Sessions",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    env_path = _find_env_file()
    env_data = _read_env_ini(env_path)
    connections_dict = env_data.get('connections', {})
    
    # If target is specified, attach directly
    if target:
        # Handle cleanup aliases first (before session lookup)
        if target.lower() in ('c', 'cleanup'):
            _do_session_cleanup()
            raise typer.Exit()
        
        # Try as number first
        try:
            idx = int(target)
            if 1 <= idx <= len(sessions):
                s = sessions[idx - 1]
                conn_data = connections_dict.get(s['key'], {})
                _do_attach(s['key'], conn_data, s['is_current'])
                raise typer.Exit()
            else:
                OutputHelper.print_panel(
                    f"Invalid session number: {idx}\n"
                    f"Valid range: 1-{len(sessions)}",
                    title="Error",
                    border_style="red"
                )
                raise typer.Exit(1)
        except ValueError:
            pass
        
        # Try as connection name
        found_key = None
        for key in connections_dict:
            if key.upper() == target.upper():
                found_key = key
                break
        
        if found_key:
            conn_data = connections_dict[found_key]
            # Find if it's current (case-insensitive comparison)
            current_session = _read_session()
            current_conn = current_session.get('connection', '') if current_session else ''
            is_current = current_conn.upper() == found_key.upper()
            _do_attach(found_key, conn_data, is_current)
            raise typer.Exit()
        else:
            OutputHelper.print_panel(
                f"Session [bright_red]{target}[/bright_red] not found.\n"
                "Run [bright_green]replx session[/bright_green] to see available sessions.",
                title="Session Not Found",
                border_style="red"
            )
            raise typer.Exit(1)
    
    # Interactive mode: show list and prompt
    _print_session_list(sessions)
    
    # Find default session index
    default_idx = None
    for s in sessions:
        if s['is_default']:
            default_idx = s['index']
            break
    
    # Check if there are any active sessions
    active_sessions = [s for s in sessions if s['is_active']]
    if not active_sessions:
        console = Console(width=CONSOLE_WIDTH)
        console.print("\n[dim]No active sessions to attach. Run 'replx --port PORT setup' first.[/dim]")
        raise typer.Exit()
    
    # Prompt for selection
    console = Console(width=CONSOLE_WIDTH)
    prompt_text = f"\nSelect [1-{len(sessions)}]"
    if default_idx:
        prompt_text += f", Enter={default_idx}"
    prompt_text += ", q=quit: "
    
    try:
        console.print(prompt_text, end="")
        choice = input().strip()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled[/dim]")
        raise typer.Exit()
    
    if choice.lower() == 'q' or choice.lower() == 'quit':
        raise typer.Exit()
    
    # Default selection
    if not choice and default_idx:
        choice = str(default_idx)
    
    if not choice:
        raise typer.Exit()
    
    # Parse selection
    try:
        idx = int(choice)
        if 1 <= idx <= len(sessions):
            s = sessions[idx - 1]
            if not s['is_active']:
                OutputHelper.print_panel(
                    f"Session [bright_yellow]{s['key']}[/bright_yellow] is not active.\n"
                    f"Run [bright_green]replx --port {s['key']} setup[/bright_green] to start it.",
                    title="Session Not Active",
                    border_style="yellow"
                )
                raise typer.Exit(1)
            conn_data = connections_dict.get(s['key'], {})
            _do_attach(s['key'], conn_data, s['is_current'])
        else:
            OutputHelper.print_panel(
                f"Invalid selection: {idx}",
                title="Error",
                border_style="red"
            )
            raise typer.Exit(1)
    except ValueError:
        OutputHelper.print_panel(
            f"Invalid input: {choice}",
            title="Error",
            border_style="red"
        )
        raise typer.Exit(1)

def _do_session_cleanup():
    """
    Perform session cleanup logic.
    """
    # Get all sessions first
    all_sessions = _list_all_sessions()
    
    if not all_sessions:
        OutputHelper.print_panel(
            "No session files found.",
            title="Cleanup",
            border_style="dim"
        )
        return
    
    # Count valid and orphaned
    valid_count = sum(1 for s in all_sessions if s['valid'])
    orphaned_count = sum(1 for s in all_sessions if not s['valid'])
    
    if orphaned_count == 0:
        OutputHelper.print_panel(
            f"No orphaned sessions found.\n"
            f"Active sessions: {valid_count}",
            title="Cleanup",
            border_style="green"
        )
        return
    
    # Clean up orphaned sessions
    cleaned = _cleanup_orphaned_sessions()
    
    OutputHelper.print_panel(
        f"Cleaned up [bright_green]{len(cleaned)}[/bright_green] orphaned session(s).\n"
        f"Active sessions: {valid_count}",
        title="✓ Cleanup Complete",
        border_style="green"
    )

@session_app.command("cleanup")
def session_cleanup(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Clean up orphaned session files.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Clean up orphaned session files.

[bold cyan]Usage:[/bold cyan]
  replx session cleanup
  replx session c

[bold cyan]Description:[/bold cyan]
  Removes session files for terminals that no longer exist.
  Session files track which connection each terminal is using.
  
  Orphaned sessions are automatically cleaned during normal operation,
  but you can run this command to clean them up manually."""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _do_session_cleanup()

@session_app.command("c", hidden=True)
def session_cleanup_short():
    """
    Clean up orphaned session files (short alias).
    """
    _do_session_cleanup()

# ============================================================================
# Legacy commands (to be removed - keeping for reference during transition)
# ============================================================================

@app.command(hidden=True)
def connections(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    List all registered connections in the workspace.
    Shows connection configurations from .replx file and active sessions.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
List all registered connections in the workspace.

[bold cyan]Usage:[/bold cyan]
  replx connections

[bold cyan]Description:[/bold cyan]
  Shows all connection configurations from the .replx file
  and indicates which ones have active agents.

[bold cyan]Output:[/bold cyan]
  • [green]✓[/green] Connection has an active agent
  • [yellow]★[/yellow] Default connection
  • Agent port and device info for each connection"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    env_path = _find_env_file()
    
    if not env_path:
        OutputHelper.print_panel(
            "No workspace found.\n"
            "Run [bright_green]replx --port PORT setup[/bright_green] to configure.",
            title="No Connections",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    env_data = _read_env_ini(env_path)
    default_conn = env_data.get('default')
    connections_dict = env_data.get('connections', {})
    
    if not connections_dict:
        OutputHelper.print_panel(
            "No connections registered.\n"
            "Run [bright_green]replx --port PORT setup[/bright_green] to add a connection.",
            title="No Connections",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    # Build content lines
    content_lines = []
    
    for conn_key, conn_data in connections_dict.items():
        # Status icon
        is_default = conn_key == default_conn
        agent_port = conn_data.get('agent_port', DEFAULT_AGENT_PORT)
        
        # Check agent running AND board connected
        is_agent_running = AgentClient.is_agent_running(port=agent_port)
        is_board_connected = False
        
        if is_agent_running:
            try:
                with AgentClient(port=agent_port) as client:
                    status = client.send_command('status', timeout=1.0)
                    is_board_connected = status.get('connected', False)
            except Exception:
                is_board_connected = False
        
        # Session is truly active only if board is connected
        is_active = is_agent_running and is_board_connected
        
        icon = "  "
        if is_default and is_active:
            icon = "[green]★[/green] "
        elif is_default:
            icon = "[yellow]★[/yellow] "
        elif is_active:
            icon = "[green]✓[/green] "
        
        # Connection name styling
        if is_active:
            conn_display = f"[bright_green]{conn_key}[/bright_green]"
        else:
            conn_display = f"[dim]{conn_key}[/dim]"
        
        # Status text - distinguish between agent running but board disconnected
        if is_active:
            status_text = "[green]connected[/green]"
        elif is_agent_running and not is_board_connected:
            status_text = "[yellow]disconnected[/yellow]"
        else:
            status_text = "[dim]inactive[/dim]"
        
        device = conn_data.get('device', '-') or '-'
        core = conn_data.get('core', '-') or '-'
        
        content_lines.append(f"{icon}{conn_display} - {device} on {core} (port {agent_port}) {status_text}")
    
    # Add footer info
    content_lines.append("")
    if default_conn:
        content_lines.append(f"[dim]Default: {default_conn}[/dim]")
    
    session = _read_session()
    if session:
        content_lines.append(f"[dim]This terminal: {session.get('connection')} (port {session.get('agent_port')})[/dim]")
    
    OutputHelper.print_panel(
        "\n".join(content_lines),
        title="Registered Connections",
        border_style="cyan"
    )

@app.command(hidden=True)
def attach(
    connection: Optional[str] = typer.Argument(None, help="Connection to attach to (e.g., COM3, 192.168.1.10)"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Attach this terminal to an existing connection.
    Use this to connect to a device that's already running in another terminal.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Attach this terminal to an existing connection.

[bold cyan]Usage:[/bold cyan]
  replx attach [yellow][CONNECTION][/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]CONNECTION[/yellow]  Connection to attach to (e.g., COM3, 192.168.1.10)
                If not specified, shows available connections.

[bold cyan]Description:[/bold cyan]
  Links this terminal to a device that's already set up in another terminal.
  The agent must already be running for the connection.

[bold cyan]Examples:[/bold cyan]
  replx attach COM3          [dim]# Attach to COM3's session[/dim]
  replx attach 192.168.1.10  [dim]# Attach to WebREPL device[/dim]
  replx attach               [dim]# Show available connections[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    env_path = _find_env_file()
    
    if not env_path:
        OutputHelper.print_panel(
            "No workspace found.\n"
            "Run [bright_green]replx --port PORT setup[/bright_green] first.",
            title="No Workspace",
            border_style="red"
        )
        raise typer.Exit(1)
    
    env_data = _read_env_ini(env_path)
    connections_dict = env_data.get('connections', {})
    
    if not connections_dict:
        OutputHelper.print_panel(
            "No connections available.\n"
            "Run [bright_green]replx --port PORT setup[/bright_green] first.",
            title="No Connections",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # If no connection specified, show available active connections
    if not connection:
        active_connections = []
        for conn_key, conn_data in connections_dict.items():
            agent_port = conn_data.get('agent_port', DEFAULT_AGENT_PORT)
            if AgentClient.is_agent_running(port=agent_port):
                active_connections.append((conn_key, conn_data))
        
        if not active_connections:
            OutputHelper.print_panel(
                "No active connections found.\n"
                "Run [bright_green]replx connections[/bright_green] to see all configured connections.",
                title="No Active Connections",
                border_style="yellow"
            )
            raise typer.Exit(1)
        
        content = "Active connections:\n"
        for conn_key, conn_data in active_connections:
            device = conn_data.get('device', 'unknown')
            port = conn_data.get('agent_port', DEFAULT_AGENT_PORT)
            content += f"  [bright_green]{conn_key}[/bright_green] - {device} (port {port})\n"
        content += "\nRun [bright_blue]replx attach CONNECTION[/bright_blue] to attach."
        
        OutputHelper.print_panel(
            content,
            title="Available Connections",
            border_style="blue"
        )
        raise typer.Exit()
    
    # Find the connection (case-insensitive for serial ports)
    found_key = None
    for key in connections_dict:
        if key.upper() == connection.upper():
            found_key = key
            break
    
    if not found_key:
        OutputHelper.print_panel(
            f"Connection [bright_red]{connection}[/bright_red] not found.\n"
            "Run [bright_green]replx connections[/bright_green] to see available connections.",
            title="Connection Not Found",
            border_style="red"
        )
        raise typer.Exit(1)
    
    conn_data = connections_dict[found_key]
    agent_port = conn_data.get('agent_port', DEFAULT_AGENT_PORT)
    
    # Check if agent is running
    if not AgentClient.is_agent_running(port=agent_port):
        OutputHelper.print_panel(
            f"Connection [bright_yellow]{found_key}[/bright_yellow] is not active.\n"
            f"Run [bright_green]replx --port {found_key} setup[/bright_green] to start it.",
            title="Connection Not Active",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    # Get status from agent
    try:
        with AgentClient(port=agent_port) as client:
            status = client.send_command('status', timeout=2.0)
        
        device = status.get('device', conn_data.get('device', 'unknown'))
        core = status.get('core', conn_data.get('core', 'unknown'))
        version = status.get('version', '?')
        
        # Update session file
        _write_session(found_key, agent_port)
        
        # Update local state
        STATE.device = device
        STATE.core = core
        STATE.version = version
        
        OutputHelper.print_panel(
            f"Attached to [bright_green]{found_key}[/bright_green]\n"
            f"Device: [bright_yellow]{device}[/bright_yellow] on [bright_green]{core}[/bright_green]\n"
            f"Agent Port: [bright_cyan]{agent_port}[/bright_cyan]\n"
            f"Version: [yellow]{version}[/yellow]",
            title="Attached",
            border_style="green"
        )
    except Exception as e:
        OutputHelper.print_panel(
            f"Failed to attach to {found_key}: {str(e)}",
            title="Attach Error",
            border_style="red"
        )
        raise typer.Exit(1)

@app.command(hidden=True)
def cleanup(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Clean up orphaned session files.
    Removes session files for terminals that no longer exist.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Clean up orphaned session files.

[bold cyan]Usage:[/bold cyan]
  replx cleanup

[bold cyan]Description:[/bold cyan]
  Removes session files for terminals that no longer exist.
  Session files track which connection each terminal is using.
  
  Orphaned sessions are automatically cleaned during normal operation,
  but you can run this command to clean them up manually."""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    # Get all sessions first
    all_sessions = _list_all_sessions()
    
    if not all_sessions:
        OutputHelper.print_panel(
            "No session files found.",
            title="Cleanup",
            border_style="dim"
        )
        raise typer.Exit()
    
    # Count valid and orphaned
    valid_count = sum(1 for s in all_sessions if s['valid'])
    orphaned_count = sum(1 for s in all_sessions if not s['valid'])
    
    if orphaned_count == 0:
        OutputHelper.print_panel(
            f"No orphaned sessions found.\n"
            f"Active sessions: {valid_count}",
            title="Cleanup",
            border_style="green"
        )
        raise typer.Exit()
    
    # Clean up orphaned sessions
    cleaned = _cleanup_orphaned_sessions()
    
    OutputHelper.print_panel(
        f"Cleaned up [bright_green]{len(cleaned)}[/bright_green] orphaned session(s).\n"
        f"Active sessions: {valid_count}",
        title="Cleanup Complete",
        border_style="green"
    )

@app.command()
def get(
    args: Optional[list[str]] = typer.Argument(None, help="Remote file(s) and local destination"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Download file(s) or directory from the connected device to the local filesystem.
    Last argument is the local destination path.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Download file(s) or directory from the connected device to the local filesystem.
Last argument is the local destination path.

[bold cyan]Usage:[/bold cyan]
  replx get [yellow]REMOTE... LOCAL[/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]REMOTE...[/yellow]  Remote file(s) or directory path(s) [red][required][/red]
  [yellow]LOCAL[/yellow]      Local destination path [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx get /lib/test.py ./           [dim]# Download to current dir[/dim]
  replx get /lib ./mylib              [dim]# Download directory[/dim]
  replx get /lib/a.py /lib/b.py ./    [dim]# Download multiple files[/dim]
  replx get /*.py ./backup            [dim]# Download all .py files[/dim]
  replx get audi*.py ./               [dim]# Download audio*.py files[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    status = _ensure_connected()
    device_root_fs = status.get('device_root_fs', '/')
    
    if not args or len(args) < 2:
        OutputHelper.print_panel(
            "Missing required arguments.\n\n"
            "[bold cyan]Usage:[/bold cyan] replx get [yellow]REMOTE... LOCAL[/yellow]\n\n"
            "At least 2 arguments required: remote file(s) and local destination.",
            title="Download Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Get raw arguments from sys.argv to avoid Typer's shell expansion
    cmd_idx = next((i for i, arg in enumerate(sys.argv) if arg == 'get'), None)
    if cmd_idx is not None and cmd_idx + 1 < len(sys.argv):
        raw_args = []
        for arg in sys.argv[cmd_idx + 1:]:
            if arg.startswith('-'):
                continue
            raw_args.append(arg)
        if len(raw_args) >= 2:
            args = raw_args
    
    # Last argument is local destination
    local = args[-1]
    remotes = args[:-1]
    
    # Helper function to normalize remote path
    def normalize_remote(path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        return path
    
    # Use AgentClient for all operations
    client = AgentClient(port=_get_agent_port())
    
    # Expand wildcards and collect all files to download
    files_to_download = []
    
    for remote_pattern in remotes:
        remote = normalize_remote(remote_pattern)
        
        # Check for wildcards
        if '*' in remote_pattern or '?' in remote_pattern:
            # Extract directory and pattern
            dir_path = posixpath.dirname(remote) or '/'
            basename_pattern = posixpath.basename(remote)
            
            try:
                result = client.send_command('ls', path=dir_path, detailed=True)
                items = [(item['name'], item['size'], item['is_dir']) for item in result.get('items', [])]
                
                for name, size, is_dir in items:
                    if fnmatch.fnmatch(name, basename_pattern):
                        full_path = posixpath.join(dir_path, name)
                        files_to_download.append((full_path, name, is_dir))
            except Exception as e:
                OutputHelper.print_panel(
                    f"[red]{remote_pattern}[/red] - pattern did not match any files.",
                    title="Download Failed",
                    border_style="red"
                )
                continue
        else:
            # Single file/directory
            try:
                result = client.send_command('is_dir', path=remote)
                is_dir = result.get('is_dir', False)
                basename = posixpath.basename(remote.rstrip('/'))
                files_to_download.append((remote, basename, is_dir))
            except Exception as e:
                display_remote = remote.replace(device_root_fs, "", 1)
                OutputHelper.print_panel(
                    f"[red]{display_remote}[/red] does not exist.",
                    title="Download Failed",
                    border_style="red"
                )
                continue
    
    if not files_to_download:
        OutputHelper.print_panel(
            "No files to download.",
            title="Download",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    # Download files
    total_files = len(files_to_download)
    success_count = 0
    
    if total_files == 1:
        # Single file/directory - use original behavior
        remote, basename, is_dir = files_to_download[0]
        display_remote = remote.replace(device_root_fs, "", 1)
        
        # Determine local destination
        if os.path.exists(local) and os.path.isdir(local):
            local_path = os.path.join(local, basename)
        else:
            local_path = local
        
        item_type = "Directory" if is_dir else "File"
        
        try:
            if is_dir:
                # Use streaming directory download from server
                progress_state = {"current": 0, "total": 0, "file": "", "status": "starting"}
                
                def progress_callback(progress_data):
                    progress_state.update(progress_data)
                
                # Start streaming download
                with Live(OutputHelper.create_progress_panel(0, 1, title=f"Downloading {basename}", message="Scanning directory..."), console=OutputHelper._console, refresh_per_second=10) as live:
                    import threading
                    import time
                    
                    result_holder = {"result": None, "error": None, "done": False}
                    
                    def stream_callback(data):
                        progress_state.update(data)
                    
                    def download_task():
                        try:
                            result = client.send_command_streaming(
                                'getdir_to_local',
                                remote_path=remote,
                                local_path=local_path,
                                progress_callback=stream_callback,
                                timeout=300
                            )
                            result_holder["result"] = result
                        except Exception as e:
                            result_holder["error"] = str(e)
                        finally:
                            result_holder["done"] = True
                    
                    # Run download in background thread
                    download_thread = threading.Thread(target=download_task, daemon=True)
                    download_thread.start()
                    
                    # Update progress display
                    while not result_holder["done"]:
                        current = progress_state.get("current", 0)
                        total = progress_state.get("total", 1) or 1
                        file = progress_state.get("file", "")
                        status = progress_state.get("status", "")
                        
                        if status == "starting":
                            message = "Scanning directory..."
                        elif status == "downloading" and file:
                            message = f"Downloading {file}..."
                        else:
                            message = ""
                        
                        live.update(OutputHelper.create_progress_panel(current, total, title=f"Downloading {basename}", message=message))
                        time.sleep(0.05)
                    
                    # Final update
                    live.update(OutputHelper.create_progress_panel(
                        progress_state.get("current", 0), 
                        progress_state.get("total", 0) or 1, 
                        title=f"Downloading {basename}"
                    ))
                    
                    if result_holder["error"]:
                        raise Exception(result_holder["error"])
            else:
                # Single file - simple download with progress
                file_count = 1
                with Live(OutputHelper.create_progress_panel(0, file_count, title=f"Downloading {basename}", message=f"Downloading file..."), console=OutputHelper._console, refresh_per_second=10) as live:
                    result = client.send_command('get_to_local', remote_path=remote, local_path=local_path, timeout=60)
                    live.update(OutputHelper.create_progress_panel(1, 1, title=f"Downloading {basename}"))
            
            OutputHelper.print_panel(
                f"Downloaded [bright_blue]{display_remote}[/bright_blue]\nto [green]{local_path}[/green]",
                title="Download Complete",
                border_style="green"
            )
        except Exception as e:
            OutputHelper.print_panel(
                f"Download failed: [red]{str(e)}[/red]",
                title="Download Failed",
                border_style="red"
            )
            raise typer.Exit(1)
    else:
        # Multiple files - ensure destination is a directory
        if not os.path.exists(local):
            os.makedirs(local)
        elif not os.path.isdir(local):
            OutputHelper.print_panel(
                f"Destination [red]{local}[/red] must be a directory when downloading multiple files.",
                title="Download Failed",
                border_style="red"
            )
            raise typer.Exit(1)
        
        with Live(OutputHelper.create_progress_panel(0, total_files, title=f"Downloading {total_files} item(s)", message="Starting..."), console=OutputHelper._console, refresh_per_second=10) as live:
            for idx, (remote, basename, is_dir) in enumerate(files_to_download):
                display_remote = remote.replace(device_root_fs, "", 1)
                live.update(OutputHelper.create_progress_panel(idx, total_files, title=f"Downloading {total_files} item(s)", message=f"Downloading {display_remote}..."))
                
                local_path = os.path.join(local, basename)
                
                try:
                    if is_dir:
                        # Use streaming for directory download
                        result = client.send_command_streaming(
                            'getdir_to_local', 
                            remote_path=remote, 
                            local_path=local_path, 
                            timeout=300
                        )
                    else:
                        result = client.send_command('get_to_local', remote_path=remote, local_path=local_path, timeout=60)
                    success_count += 1
                except Exception as e:
                    OutputHelper._console.print(f"[red]Failed to download {display_remote}: {str(e)}[/red]")
            
            live.update(OutputHelper.create_progress_panel(total_files, total_files, title=f"Downloading {total_files} item(s)"))
        
        OutputHelper.print_panel(
            f"Downloaded [green]{success_count}[/green] out of {total_files} file(s)\nto [green]{local}[/green]",
            title="Download Complete",
            border_style="green" if success_count == total_files else "yellow"
        )


@app.command(name="cat")
def cat(
    remote: str = typer.Argument("", help="Remote file path"),
    encoding: str = typer.Option("utf-8", help="File encoding for text files"),
    number: bool = typer.Option(False, "-n", "--number", help="Show line numbers"),
    lines: Optional[str] = typer.Option(None, "-L", "--lines", help="Range: lines (text) or bytes (binary)"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Display the content of a file from the connected device.
    Text files are displayed as-is, binary files are shown in hex format.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Display the content of a file from the connected device.
Text files are displayed as-is, binary files are shown in hex format.

[bold cyan]Usage:[/bold cyan]
  replx cat [[cyan]OPTIONS[/cyan]] [yellow]REMOTE[/yellow]

[bold cyan]Options:[/bold cyan]
  --encoding [green]TEXT[/green]       File encoding [dim][default: utf-8][/dim]
  -n, --number          Show line numbers [dim](text files only)[/dim]
  -L, --lines [green]N:M[/green]       Line range [dim](text)[/dim] or byte range [dim](binary)[/dim]

[bold cyan]Arguments:[/bold cyan]
  [yellow]remote[/yellow]      Remote file path [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  [dim]# Text files[/dim]
  replx cat /lib/main.py             [dim]# Show file contents[/dim]
  replx cat -n /lib/main.py          [dim]# Show with line numbers[/dim]
  replx cat -L 10:20 /lib/main.py    [dim]# Show lines 10 to 20[/dim]
  replx cat -L :20 /lib/main.py      [dim]# Show first 20 lines[/dim]
  
  [dim]# Binary files[/dim]
  replx cat -L 0:256 /lib/file.mpy   [dim]# Show first 256 bytes[/dim]
  replx cat -L 100:+64 /lib/file.mpy [dim]# Show 64 bytes from offset 100[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    if not remote:
        typer.echo("Error: Missing required argument 'REMOTE'.", err=True)
        raise typer.Exit(1)
    
    # Normalize path
    if not remote.startswith('/'):
        remote = '/' + remote
    
    display_remote = remote.replace('/', '', 1) if remote.startswith('/') else remote
    
    # Use agent to get file content
    client = AgentClient(port=_get_agent_port())
    
    try:
        result = client.send_command('cat', path=remote)
        content = result.get('content', '')
        is_binary = result.get('is_binary', False)
        file_size = result.get('size', 0)
    except Exception as e:
        error_msg = str(e)
        if 'Not connected' in error_msg:
            OutputHelper.print_panel(
                "Not connected to any device.\n\nRun [bright_green]replx connect --port COM3[/bright_green] first.",
                title="Connection Required",
                border_style="red"
            )
        elif 'is a directory' in error_msg.lower():
            OutputHelper.print_panel(
                f"[red]{display_remote}[/red] is a directory, not a file.",
                title="Read Failed",
                border_style="red"
            )
        else:
            OutputHelper.print_panel(
                f"[red]{display_remote}[/red] does not exist.",
                title="Read Failed",
                border_style="red"
            )
        raise typer.Exit(1)
    
    if is_binary:
        # Binary file - content is hex string from server, convert back to bytes
        raw_bytes = bytes.fromhex(content)
        total_bytes = len(raw_bytes)
        start_byte = 0
        end_byte = total_bytes
        
        # Parse byte range for binary files
        if lines:
            try:
                if ':' not in lines:
                    raise ValueError("Invalid format")
                parts = lines.split(':')
                if len(parts) != 2:
                    raise ValueError("Invalid format")
                
                # Parse start byte
                if parts[0]:
                    start_byte = int(parts[0])
                    if start_byte < 0:
                        start_byte = 0
                
                # Parse end byte
                if parts[1]:
                    if parts[1].startswith('+'):
                        # Relative: N:+M means M bytes from N
                        count = int(parts[1][1:])
                        end_byte = start_byte + count
                    else:
                        # Absolute: N:M
                        end_byte = int(parts[1])
                
                # Clamp to valid range
                start_byte = max(0, min(start_byte, total_bytes))
                end_byte = max(start_byte, min(end_byte, total_bytes))
            except (ValueError, IndexError):
                OutputHelper.print_panel(
                    f"Invalid byte range format: [red]{lines}[/red]\nFor binary files, use N:M (byte range)",
                    title="Invalid Option",
                    border_style="red"
                )
                raise typer.Exit(1)
        
        # Extract byte range
        data = raw_bytes[start_byte:end_byte]
        
        # Format hex dump: 16 bytes per line with ASCII representation
        # Align to 16-byte boundaries and show -- for bytes outside the range
        from rich.text import Text
        hex_output = Text()
        
        # Calculate the first and last line boundaries (aligned to 16 bytes)
        first_line_start = (start_byte // 16) * 16
        last_line_end = ((end_byte + 15) // 16) * 16
        
        for line_offset in range(first_line_start, last_line_end, 16):
            # Add offset
            hex_output.append(f"{line_offset:08x}", style="cyan")
            hex_output.append("  ")
            
            # Hex part
            hex_chars = []
            ascii_chars = []
            
            for byte_offset in range(line_offset, line_offset + 16):
                if start_byte <= byte_offset < end_byte:
                    # Byte is within range - show actual data
                    data_index = byte_offset - start_byte
                    b = data[data_index]
                    hex_chars.append((f'{b:02x}', "bright_green"))
                    # For ASCII part: printable chars or dot
                    if 32 <= b < 127:
                        ascii_chars.append((chr(b), None))
                    else:
                        ascii_chars.append((".", "dim"))
                else:
                    # Byte is outside range - show placeholder
                    hex_chars.append(("--", "dim"))
                    ascii_chars.append((" ", None))
            
            # Add hex bytes with spaces
            for i, (h, style) in enumerate(hex_chars):
                if i > 0:
                    hex_output.append(" ")
                hex_output.append(h, style=style)
            
            hex_output.append("   ")
            
            # Add ASCII chars
            for c, style in ascii_chars:
                hex_output.append(c, style=style)
            
            hex_output.append("\n")
        
        range_info = f" (bytes {start_byte}-{end_byte})" if lines else f" ({total_bytes} bytes)"
        title = f"Binary File (Hex): {display_remote}{range_info}"
        
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        console.print(Panel(
            hex_output,
            title=title,
            border_style="blue",
            box=get_panel_box(),
            width=CONSOLE_WIDTH
        ))
        return  # Binary file handled, exit early
    else:
        # Text file - content is string from server
        text_content = content
        content_lines = text_content.split('\n')
        total_lines = len(content_lines)
        
        # Apply line range if specified
        start_line = 1
        end_line = total_lines
        if lines:
            try:
                if ':' in lines:
                    parts = lines.split(':')
                    if parts[0]:
                        start_line = max(1, int(parts[0]))
                    if parts[1]:
                        if parts[1].startswith('+'):
                            end_line = start_line + int(parts[1][1:]) - 1
                        else:
                            end_line = int(parts[1])
                    end_line = min(end_line, total_lines)
            except:
                pass
        
        display_lines = content_lines[start_line-1:end_line]
        
        # Add line numbers if requested
        if number:
            width = len(str(start_line + len(display_lines) - 1))
            formatted = []
            for idx, line in enumerate(display_lines):
                line_num = start_line + idx
                formatted.append(f"{line_num:>{width}}: {line}")
            display_content = '\n'.join(formatted)
        else:
            display_content = '\n'.join(display_lines)
        
        range_info = f" (lines {start_line}-{end_line})" if lines else f" ({total_lines} lines)"
        title = f"File Content: {display_remote}{range_info}"
    
    syntax_extensions = {
        '.py': 'python',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
    }
    
    # Get file extension
    import os as os_module
    _, ext = os_module.path.splitext(remote.lower())
    language = syntax_extensions.get(ext)
    
    # Use syntax highlighting for supported file types (text files only)
    if language and not is_binary:
        from rich.syntax import Syntax
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        
        # Create syntax-highlighted content
        syntax = Syntax(
            display_content if not number else '\n'.join(display_lines),
            language,
            theme="dracula", #monokai, dracula, one-dark
            line_numbers=number,
            start_line=start_line if number else 1,
            word_wrap=False
        )
        
        # Print in a panel
        console.print(Panel(
            syntax,
            title=title,
            border_style="blue",
            box=get_panel_box(),
            width=CONSOLE_WIDTH
        ))
    else:
        # Plain text or binary - use existing panel
        OutputHelper.print_panel(
            display_content,
            title=title,
            border_style="blue"
        )


@app.command()
@app.command()
def info(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Show device information including memory and filesystem status.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Show device information including memory and filesystem status.

[bold cyan]Usage:[/bold cyan]
  replx info

[bold cyan]Examples:[/bold cyan]
  replx info                         [dim]# Display device info[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    status = _ensure_connected()
    
    try:
        client = AgentClient(port=_get_agent_port())
        
        # Get memory info
        mem_result = client.send_command('mem')
        mem = mem_result.get('mem')
        
        # Get filesystem info
        df_result = client.send_command('df')
        
        # Build output with visual bars
        lines = []
        
        # Device info header
        device = status.get('device', 'Unknown')
        port = status.get('port', '')
        target = status.get('target', '')
        core = status.get('core', 'Unknown')
        version = status.get('version', '')
        
        lines.append(f"[bold bright_white][#5CB8C2]󰍛[/#5CB8C2] {device}[/bold bright_white] [dim]({core})[/dim]")
        if target:
            lines.append(f"   [dim]WebREPL:[/dim] {target}")
        else:
            lines.append(f"   [dim]Serial:[/dim]  {port}")
        if version:
            lines.append(f"   [dim]Version:[/dim] {version}")
        lines.append("")
        
        # Helper function to create visual bar
        def make_bar(used_pct, width=30):
            filled = int(width * used_pct / 100)
            empty = width - filled
            if used_pct < 50:
                color = "green"
            elif used_pct < 80:
                color = "yellow"
            else:
                color = "red"
            return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
        
        # Memory info
        if mem:
            mem_total = mem[2]
            mem_used = mem[1]
            mem_free = mem[0]
            mem_pct = mem[3]
            lines.append(f"[bold cyan][#87C05A]󰍛[/#87C05A] Memory[/bold cyan]")
            lines.append(f"   {make_bar(mem_pct)} [bold]{mem_pct:.1f}%[/bold]")
            lines.append(f"   [dim]Used:[/dim]  {mem_used//1024:>5} KB  [dim]Free:[/dim] {mem_free//1024:>5} KB  [dim]Total:[/dim] {mem_total//1024:>5} KB")
        else:
            lines.append("[bold cyan][#87C05A]󰍛[/#87C05A] Memory[/bold cyan]  [dim]unavailable[/dim]")
        
        lines.append("")
        
        # Filesystem info
        if df_result:
            fs_total = df_result.get('total', 0)
            fs_used = df_result.get('used', 0)
            fs_free = df_result.get('free', 0)
            fs_pct = df_result.get('percent', 0)
            lines.append(f"[bold cyan][#D98C53]󰋊[/#D98C53] Storage[/bold cyan]")
            lines.append(f"   {make_bar(fs_pct)} [bold]{fs_pct:.1f}%[/bold]")
            lines.append(f"   [dim]Used:[/dim]  {fs_used//1024:>5} KB  [dim]Free:[/dim] {fs_free//1024:>5} KB  [dim]Total:[/dim] {fs_total//1024:>5} KB")
        else:
            lines.append("[bold cyan][#D98C53]󰋊[/#D98C53] Storage[/bold cyan]  [dim]unavailable[/dim]")
        
        OutputHelper.print_panel("\n".join(lines), title="Device Information", border_style="bright_blue")
        
    except Exception as e:
        OutputHelper.print_panel(f"Error: {str(e)}", title="Error", border_style="red")
        raise typer.Exit(1)


@app.command()
def mkdir(
    remotes: Optional[list[str]] = typer.Argument(None, help="Directories to create"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Create one or more directories on the connected device.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Create one or more directories on the connected device.

[bold cyan]Usage:[/bold cyan]
  replx mkdir [yellow]REMOTES...[/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]remotes[/yellow]     Directories to create [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx mkdir /lib                   [dim]# Create single directory[/dim]
  replx mkdir /lib /tests /docs      [dim]# Create multiple directories[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    if not remotes:
        typer.echo("Error: Missing required arguments.", err=True)
        raise typer.Exit(1)
    
    success_count = 0
    already_exist = []
    
    with AgentClient(port=_get_agent_port()) as client:
        for remote in remotes:
            # Normalize path
            if not remote.startswith('/'):
                remote = '/' + remote
            
            try:
                result = client.send_command('mkdir', path=remote)
                success_count += 1
                if len(remotes) == 1:  # Only show panel for single directory
                    OutputHelper.print_panel(
                        f"Directory [bright_blue]{remote}[/bright_blue] created successfully.",
                        title="Create Directory",
                        border_style="green"
                    )
            except Exception as e:
                error_msg = str(e)
                if 'EEXIST' in error_msg or 'exists' in error_msg.lower():
                    already_exist.append(remote)
                    if len(remotes) == 1:
                        OutputHelper.print_panel(
                            f"Directory [bright_blue]{remote}[/bright_blue] already exists.",
                            title="Create Directory",
                            border_style="yellow"
                        )
                else:
                    already_exist.append(remote)
                    if len(remotes) == 1:
                        OutputHelper.print_panel(
                            f"Failed to create [bright_blue]{remote}[/bright_blue]: {error_msg}",
                            title="Create Directory",
                            border_style="red"
                        )
    
    # Summary for multiple directories
    if len(remotes) > 1:
        if already_exist:
            OutputHelper.print_panel(
                f"Created [green]{success_count}[/green] director{'y' if success_count == 1 else 'ies'}.\nAlready exist: {', '.join(already_exist)}",
                title="Create Directories",
                border_style="yellow" if success_count > 0 else "green"
            )
        else:
            OutputHelper.print_panel(
                f"Created [green]{success_count}[/green] director{'y' if success_count == 1 else 'ies'} successfully.",
                title="Create Directories",
                border_style="green"
            )

@app.command()
def rm(
    args: Optional[list[str]] = typer.Argument(None, help="Files or directories to remove"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Remove directories recursively"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Remove files or directories from the connected device.
    Use -r option to remove directories recursively.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Remove files or directories from the connected device.
Use -r option to remove directories recursively.

[bold cyan]Usage:[/bold cyan]
  replx rm [[cyan]OPTIONS[/cyan]] [yellow]REMOTE...[/yellow]

[bold cyan]Options:[/bold cyan]
  -r, --recursive         Remove directories recursively

[bold cyan]Arguments:[/bold cyan]
  [yellow]REMOTE...[/yellow]  File(s) or directory(ies) to remove [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx rm /lib/test.py                [dim]# Remove single file[/dim]
  replx rm /lib/a.py /lib/b.py         [dim]# Remove multiple files[/dim]
  replx rm -r /lib/backup              [dim]# Remove directory recursively[/dim]
  replx rm /*.pyc                      [dim]# Remove all .pyc files[/dim]
  replx rm /lib/*.mpy                  [dim]# Remove all .mpy files in /lib[/dim]
  replx rm audi*.py                    [dim]# Remove audio.py, audioio.py, etc.[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    status = _ensure_connected()
    device_root_fs = status.get('device_root_fs', '/')
    
    # Get raw arguments from sys.argv to avoid Typer's shell expansion
    # Find 'rm' command in sys.argv
    cmd_idx = next((i for i, arg in enumerate(sys.argv) if arg == 'rm'), None)
    if cmd_idx is not None and cmd_idx + 1 < len(sys.argv):
        # Use raw arguments after 'rm' command, skipping options
        raw_args = []
        for arg in sys.argv[cmd_idx + 1:]:
            if arg.startswith('-'):
                continue
            raw_args.append(arg)
        if raw_args:
            args = raw_args
    
    if not args:
        typer.echo("Error: Missing required arguments.", err=True)
        raise typer.Exit(1)
    
    client = AgentClient(port=_get_agent_port())
    
    # Helper function to normalize path
    def normalize_path(path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        return path
    
    success_count = 0
    failed_items = []
    dir_without_r = []  # Track directories attempted without -r
    
    for pattern in args:
        remote = normalize_path(pattern)
        
        # Check for wildcards
        if '*' in pattern or '?' in pattern:
            # Extract directory and pattern
            dir_path = posixpath.dirname(remote) or '/'
            basename_pattern = posixpath.basename(remote)
            
            try:
                result = client.send_command('ls', path=dir_path, detailed=True)
                items = [(item['name'], item['size'], item['is_dir']) for item in result.get('items', [])]
                matched = False
                
                for name, size, is_dir in items:
                    if fnmatch.fnmatch(name, basename_pattern):
                        matched = True
                        full_path = posixpath.join(dir_path, name)
                        try:
                            if is_dir:
                                if not recursive:
                                    dir_without_r.append(name)
                                    continue
                                client.send_command('rmdir', path=full_path)
                            else:
                                client.send_command('rm', path=full_path)
                            success_count += 1
                        except Exception:
                            failed_items.append(name)
                
                if not matched:
                    failed_items.append(pattern)
            except Exception:
                failed_items.append(pattern)
        else:
            # Single file/directory
            try:
                is_dir_result = client.send_command('is_dir', path=remote)
                is_dir = is_dir_result.get('is_dir', False)
                
                if is_dir:
                    if not recursive:
                        display_remote = remote.replace(device_root_fs, "", 1)
                        dir_without_r.append(display_remote)
                        continue
                    client.send_command('rmdir', path=remote)
                    item_type = "Directory"
                else:
                    client.send_command('rm', path=remote)
                    item_type = "File"
                success_count += 1
                
                display_path = remote.replace(device_root_fs, "", 1)
                if len(args) == 1:  # Only show panel for single item
                    OutputHelper.print_panel(
                        f"{item_type} [bright_blue]{display_path}[/bright_blue] removed successfully.",
                        title="Remove",
                        border_style="green"
                    )
            except Exception:
                failed_items.append(pattern)
    
    # Show error for directories attempted without -r
    if dir_without_r:
        if len(dir_without_r) == 1:
            OutputHelper.print_panel(
                f"rm: [red]{dir_without_r[0]}[/red] is a directory.\n\n"
                "Use [cyan]-r[/cyan] option to remove directories recursively:\n"
                f"  replx rm -r {dir_without_r[0]}",
                title="Remove Failed",
                border_style="red"
            )
        else:
            dirs_str = "\n".join(f"  - {d}" for d in dir_without_r)
            OutputHelper.print_panel(
                f"rm: cannot remove directories (use [cyan]-r[/cyan] option):\n{dirs_str}\n\n"
                "Example: replx rm -r <directory>",
                title="Remove Failed",
                border_style="red"
            )
        if not success_count and not failed_items:
            raise typer.Exit(1)
    
    # Summary for multiple items
    if len(args) > 1 or success_count > 1:
        if failed_items:
            OutputHelper.print_panel(
                f"Removed [green]{success_count}[/green] item(s).\nFailed: {', '.join(failed_items)}",
                title="Remove Complete",
                border_style="yellow"
            )
        else:
            OutputHelper.print_panel(
                f"Removed [green]{success_count}[/green] item(s) successfully.",
                title="Remove Complete",
                border_style="green"
            )
    elif failed_items and not dir_without_r:
        remote_display = args[0].replace(device_root_fs, "", 1) if args[0].startswith(device_root_fs) else args[0]
        OutputHelper.print_panel(
            f"rm: [red]{remote_display}[/red] does not exist.",
            title="Remove Failed",
            border_style="red"
        )
        raise typer.Exit(1)
    elif failed_items:
        remote_display = args[0].replace(device_root_fs, "", 1) if args[0].startswith(device_root_fs) else args[0]
        OutputHelper.print_panel(
            f"[red]{remote_display}[/red] does not exist.",
            title="Remove",
            border_style="red"
        )

@app.command()
def cp(
    args: Optional[list[str]] = typer.Argument(None, help="Source file(s) and destination"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Copy directories recursively"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Copy file(s) or directory on the connected device.
    Last argument is the destination. Supports wildcards for source files.
    Use -r to copy directories.
    """
    # Check for custom help
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Copy file(s) or directory on the connected device.
Last argument is the destination. Supports wildcards for source files.
Use -r to copy directories.

[bold cyan]Usage:[/bold cyan]
  replx cp [[cyan]OPTIONS[/cyan]] [yellow]SOURCE... DEST[/yellow]

[bold cyan]Options:[/bold cyan]
  -r, --recursive         Copy directories recursively

[bold cyan]Arguments:[/bold cyan]
  [yellow]SOURCE...[/yellow]  Source file(s) or directory path(s) [red][required][/red]
  [yellow]DEST[/yellow]       Destination path [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx cp /lib/test.py /lib/backup.py    [dim]# Copy file[/dim]
  replx cp /lib/test.py /backup           [dim]# Copy to directory[/dim]
  replx cp x.py y.py z.py /backup         [dim]# Copy multiple files[/dim]
  replx cp *.py /backup                   [dim]# Copy all .py files[/dim]
  replx cp -r /lib /backup                [dim]# Copy directory recursively[/dim]
  replx cp -r a.py dir1 dir2 /backup      [dim]# Copy files and directories[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    if not args or len(args) < 2:
        OutputHelper.print_panel(
            "Missing required arguments.\n\n"
            "[bold cyan]Usage:[/bold cyan] replx cp [yellow]SOURCE... DEST[/yellow]\n\n"
            "At least 2 arguments required: source file(s) and destination.",
            title="Copy Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Get raw arguments from sys.argv (skip options like -r, -h)
    cmd_idx = next((i for i, arg in enumerate(sys.argv) if arg == 'cp'), None)
    if cmd_idx is not None and cmd_idx + 1 < len(sys.argv):
        raw_args = []
        for arg in sys.argv[cmd_idx + 1:]:
            # Skip options (but not file paths starting with -)
            if arg in ('-r', '--recursive', '-h', '--help'):
                continue
            raw_args.append(arg)
        if len(raw_args) >= 2:
            args = raw_args
    
    # Last argument is destination
    dest = args[-1]
    sources = args[:-1]
    
    # Use agent for cp operation
    from replx.agent.client import AgentClient
    
    client = AgentClient(port=_get_agent_port())
    
    # For single source without wildcards, use agent directly
    if len(sources) == 1 and '*' not in sources[0] and '?' not in sources[0]:
        source = sources[0]
        try:
            resp = client.send_command('cp', source=source, dest=dest, recursive=recursive)
            
            success_count = resp.get('files_count', 1) if resp.get('copied') else 0
            total_files = resp.get('files_count', 1) if 'files_count' in resp else 1
            display_source = resp.get('source', source)
            display_dest = resp.get('dest', dest)
            
            if resp.get('copied'):
                if total_files == 1:
                    OutputHelper.print_panel(
                        f"Copied [bright_blue]{display_source}[/bright_blue]\nto [green]{display_dest}[/green]",
                        title="Copy Complete",
                        border_style="green"
                    )
                else:
                    OutputHelper.print_panel(
                        f"Copied [green]{success_count}[/green] file(s)\nfrom [bright_blue]{display_source}[/bright_blue]\nto [green]{display_dest}[/green]",
                        title="Copy Complete",
                        border_style="green"
                    )
            else:
                OutputHelper.print_panel(
                    "Source directory is empty or no files to copy.",
                    title="Copy",
                    border_style="yellow"
                )
        except RuntimeError as e:
            error = str(e)
            
            if 'not found' in error.lower() or 'does not exist' in error.lower():
                OutputHelper.print_panel(
                    f"[red]{source}[/red] does not exist.",
                    title="Copy Failed",
                    border_style="red"
                )
            elif 'is a directory' in error.lower():
                OutputHelper.print_panel(
                    f"cp: [red]{source}[/red] is a directory (not copied).\n\n"
                    "Use [cyan]-r[/cyan] option to copy directories recursively:\n"
                    f"  replx cp -r {source} <destination>",
                    title="Copy Failed",
                    border_style="red"
                )
            else:
                OutputHelper.print_panel(
                    f"Copy failed: [red]{error}[/red]",
                    title="Copy Failed",
                    border_style="red"
                )
            raise typer.Exit(1)
        return
    
    # For multiple sources or wildcards, expand on client side using agent calls
    files_to_copy = []
    
    for source_pattern in sources:
        # Check for wildcards
        if '*' in source_pattern or '?' in source_pattern:
            # Extract directory and pattern
            dir_path = posixpath.dirname(source_pattern) or '/'
            pattern = posixpath.basename(source_pattern)
            
            try:
                result = client.send_command('ls', path=dir_path, detailed=True)
                items = result.get('items', []) if isinstance(result, dict) else []
                
                matched = False
                for item in items:
                    if isinstance(item, dict):
                        name = item.get('name', '')
                        is_dir = item.get('is_dir', False)
                    else:
                        name = str(item)
                        is_dir = False
                    if fnmatch.fnmatch(name, pattern):
                        full_path = posixpath.join(dir_path, name)
                        files_to_copy.append((full_path, name, is_dir))
                        matched = True
                if not matched:
                    OutputHelper.print_panel(
                        f"No files matching: [red]{source_pattern}[/red]",
                        title="Copy Failed",
                        border_style="red"
                    )
                    raise typer.Exit(1)
            except typer.Exit:
                raise
            except Exception as e:
                OutputHelper.print_panel(
                    f"Error processing pattern '{source_pattern}': {e}",
                    title="Copy Failed",
                    border_style="red"
                )
                raise typer.Exit(1)
        else:
            # Check if source exists and get info
            try:
                result = client.send_command('is_dir', path=source_pattern)
                is_dir = result if isinstance(result, bool) else result.get('is_dir', False)
            except Exception:
                OutputHelper.print_panel(
                    f"cp: [red]{source_pattern}[/red] does not exist.",
                    title="Copy Failed",
                    border_style="red"
                )
                raise typer.Exit(1)
            
            basename = posixpath.basename(source_pattern)
            
            # Check if trying to copy directory without -r
            if is_dir and not recursive:
                OutputHelper.print_panel(
                    f"cp: [red]{source_pattern}[/red] is a directory.\n"
                    f"Use [yellow]-r[/yellow] option to copy directories.",
                    title="Copy Failed",
                    border_style="red"
                )
                raise typer.Exit(1)
            files_to_copy.append((source_pattern, basename, is_dir))
    
    if not files_to_copy:
        OutputHelper.print_panel(
            "No files to copy.",
            title="Copy",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    # Check if dest is a directory (needed for multiple files)
    try:
        result = client.send_command('is_dir', path=dest)
        dest_is_dir = result if isinstance(result, bool) else result.get('is_dir', False)
    except Exception:
        dest_is_dir = False
    
    # If copying multiple files, dest must be a directory
    if len(files_to_copy) > 1 and not dest_is_dir:
        OutputHelper.print_panel(
            f"When copying multiple files, destination must be a directory.\n"
            f"Destination [red]{dest}[/red] is not a directory.",
            title="Copy Failed",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Copy each file/directory
    success_count = 0
    for source_path, basename, is_dir in files_to_copy:
        if dest_is_dir:
            target = posixpath.join(dest, basename)
        else:
            target = dest
        
        try:
            client.send_command('cp', source=source_path, dest=target, recursive=recursive)
            success_count += 1
        except Exception as e:
            OutputHelper.print_panel(
                f"Failed to copy [red]{source_path}[/red]: {e}",
                title="Copy Failed",
                border_style="red"
            )
            if success_count > 0:
                OutputHelper.print_panel(
                    f"Copied {success_count} of {len(files_to_copy)} file(s) before error.",
                    title="Partial Copy",
                    border_style="yellow"
                )
            raise typer.Exit(1)
    
    # Success message
    if success_count == 1:
        source_path = files_to_copy[0][0]
        OutputHelper.print_panel(
            f"Copied [bright_blue]{source_path}[/bright_blue]\nto [green]{dest}[/green]",
            title="Copy Complete",
            border_style="green"
        )
    else:
        OutputHelper.print_panel(
            f"Copied [green]{success_count}[/green] file(s) to [green]{dest}[/green]",
            title="Copy Complete",
            border_style="green"
        )

@app.command()
def mv(
    args: Optional[list[str]] = typer.Argument(None, help="Source file(s) and destination"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Move directories recursively"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Move/rename file(s) or directory on the connected device.
    Last argument is the destination. Supports wildcards for source files.
    Use -r to move directories.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Move/rename file(s) or directory on the connected device.
Last argument is the destination. Supports wildcards for source files.
Use -r to move directories.

[bold cyan]Usage:[/bold cyan]
  replx mv [[cyan]OPTIONS[/cyan]] [yellow]SOURCE... DEST[/yellow]

[bold cyan]Options:[/bold cyan]
  -r, --recursive         Move directories recursively

[bold cyan]Arguments:[/bold cyan]
  [yellow]SOURCE...[/yellow]  Source file(s) or directory path(s) [red][required][/red]
  [yellow]DEST[/yellow]       Destination path [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx mv /lib/old.py /lib/new.py      [dim]# Rename file[/dim]
  replx mv /lib/test.py /backup         [dim]# Move file to directory[/dim]
  replx mv x.py y.py z.py /backup       [dim]# Move multiple files[/dim]
  replx mv *.py /backup                 [dim]# Move all .py files[/dim]
  replx mv -r /lib/audio /lib/sound     [dim]# Move directory[/dim]
  replx mv -r a.py dir1 dir2 /backup    [dim]# Move files and directories[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    if not args or len(args) < 2:
        OutputHelper.print_panel(
            "Missing required arguments.\n\n"
            "[bold cyan]Usage:[/bold cyan] replx mv [yellow]SOURCE... DEST[/yellow]\n\n"
            "At least 2 arguments required: source file(s) and destination.",
            title="Move Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Get raw arguments from sys.argv (skip options like -r, -h)
    cmd_idx = next((i for i, arg in enumerate(sys.argv) if arg == 'mv'), None)
    if cmd_idx is not None and cmd_idx + 1 < len(sys.argv):
        raw_args = []
        for arg in sys.argv[cmd_idx + 1:]:
            # Skip options (but not file paths starting with -)
            if arg in ('-r', '--recursive', '-h', '--help'):
                continue
            raw_args.append(arg)
        if len(raw_args) >= 2:
            args = raw_args
    
    # Last argument is destination
    dest = args[-1]
    sources = args[:-1]
    
    # Use agent for mv operation
    from replx.agent.client import AgentClient
    
    client = AgentClient(port=_get_agent_port())
    
    # For single source without wildcards, use agent directly
    if len(sources) == 1 and '*' not in sources[0] and '?' not in sources[0]:
        source = sources[0]
        try:
            result = client.send_command('mv', source=source, dest=dest)
            display_source = result.get('source', source)
            display_dest = result.get('dest', dest)
            
            OutputHelper.print_panel(
                f"Moved [bright_blue]{display_source}[/bright_blue]\nto [green]{display_dest}[/green]",
                title="Move Complete",
                border_style="green"
            )
        except Exception as e:
            error = str(e)
            
            if 'ENOENT' in error or 'not found' in error.lower() or 'does not exist' in error.lower():
                OutputHelper.print_panel(
                    f"mv: [red]{source}[/red] does not exist.",
                    title="Move Failed",
                    border_style="red"
                )
            elif 'is a directory' in error.lower():
                OutputHelper.print_panel(
                    f"mv: [red]{source}[/red] is a directory.\n"
                    f"Use [yellow]-r[/yellow] option to move directories.",
                    title="Move Failed",
                    border_style="red"
                )
            else:
                OutputHelper.print_panel(
                    f"Move failed: {error}",
                    title="Move Failed",
                    border_style="red"
                )
            raise typer.Exit(1)
        return
    
    # For multiple sources or wildcards, expand on client side using agent calls
    files_to_move = []
    
    for source_pattern in sources:
        # Check for wildcards
        if '*' in source_pattern or '?' in source_pattern:
            import fnmatch
            # Extract directory and pattern
            dir_path = posixpath.dirname(source_pattern) or '/'
            pattern = posixpath.basename(source_pattern)
            
            try:
                result = client.send_command('ls', path=dir_path, detailed=True)
                # result is {"items": [{"name": ..., "size": ..., "is_dir": ...}, ...]}
                items = result.get('items', []) if isinstance(result, dict) else []
                
                matched = False
                for item in items:
                    if isinstance(item, dict):
                        name = item.get('name', '')
                        is_dir = item.get('is_dir', False)
                    else:
                        name = str(item)
                        is_dir = False
                    if fnmatch.fnmatch(name, pattern):
                        full_path = posixpath.join(dir_path, name)
                        files_to_move.append((full_path, name, is_dir))
                        matched = True
                if not matched:
                    OutputHelper.print_panel(
                        f"No files matching: [red]{source_pattern}[/red]",
                        title="Move Failed",
                        border_style="red"
                    )
                    raise typer.Exit(1)
            except typer.Exit:
                raise
            except Exception as e:
                OutputHelper.print_panel(
                    f"Error processing pattern '{source_pattern}': {e}",
                    title="Move Failed",
                    border_style="red"
                )
                raise typer.Exit(1)
        else:
            # Check if source exists
            try:
                result = client.send_command('is_dir', path=source_pattern)
                is_dir = result if isinstance(result, bool) else result.get('is_dir', False)
            except Exception:
                OutputHelper.print_panel(
                    f"mv: [red]{source_pattern}[/red] does not exist.",
                    title="Move Failed",
                    border_style="red"
                )
                raise typer.Exit(1)
            
            basename = posixpath.basename(source_pattern)
            
            # Check if trying to move directory without -r
            if is_dir and not recursive:
                OutputHelper.print_panel(
                    f"mv: [red]{source_pattern}[/red] is a directory.\n"
                    f"Use [yellow]-r[/yellow] option to move directories.",
                    title="Move Failed",
                    border_style="red"
                )
                raise typer.Exit(1)
            files_to_move.append((source_pattern, basename, is_dir))
    
    if not files_to_move:
        OutputHelper.print_panel(
            "No files to move.",
            title="Move",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    # Check if dest is a directory (needed for multiple files)
    try:
        result = client.send_command('is_dir', path=dest)
        dest_is_dir = result if isinstance(result, bool) else result.get('is_dir', False)
    except Exception:
        dest_is_dir = False
    
    # If moving multiple files, dest must be a directory
    if len(files_to_move) > 1 and not dest_is_dir:
        OutputHelper.print_panel(
            f"When moving multiple files, destination must be a directory.\n"
            f"Destination [red]{dest}[/red] is not a directory.",
            title="Move Failed",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Move files using agent
    success_count = 0
    failed_items = []
    
    for source, basename, is_dir in files_to_move:
        # Determine final destination
        if dest_is_dir:
            final_dest = posixpath.join(dest, basename)
        else:
            final_dest = dest
        
        try:
            client.send_command('mv', source=source, dest=final_dest)
            success_count += 1
        except Exception as e:
            failed_items.append((source, str(e)))
    
    # Summary
    if len(files_to_move) == 1 and success_count == 1:
        source, basename, is_dir = files_to_move[0]
        display_dest = posixpath.join(dest, basename) if dest_is_dir else dest
        item_type = "Directory" if is_dir else "File"
        OutputHelper.print_panel(
            f"Moved [bright_blue]{source}[/bright_blue]\nto [green]{display_dest}[/green]",
            title=f"Move Complete ({item_type})",
            border_style="green"
        )
    elif success_count > 0:
        if failed_items:
            fail_list = "\n".join([f"  • {src}" for src, _ in failed_items])
            OutputHelper.print_panel(
                f"Moved [green]{success_count}[/green] out of {len(files_to_move)} file(s)\n"
                f"to [green]{dest}[/green]\n\n"
                f"Failed:\n{fail_list}",
                title="Move Partially Complete",
                border_style="yellow"
            )
        else:
            OutputHelper.print_panel(
                f"Moved [green]{success_count}[/green] file(s)\nto [green]{dest}[/green]",
                title="Move Complete",
                border_style="green"
            )
    else:
        fail_list = "\n".join([f"  • {src}: {err}" for src, err in failed_items])
        OutputHelper.print_panel(
            f"Failed to move files:\n{fail_list}",
            title="Move Failed",
            border_style="red"
        )
        raise typer.Exit(1)

@app.command()
def touch(
    remotes: Optional[list[str]] = typer.Argument(None, help="Files to create"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Create one or more empty files on the connected device.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Create one or more empty files on the connected device.

[bold cyan]Usage:[/bold cyan]
  replx touch [yellow]REMOTES...[/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]remotes[/yellow]     Files to create [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx touch /lib/test.py           [dim]# Create single file[/dim]
  replx touch /a.py /b.py /c.py      [dim]# Create multiple files[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    if not remotes:
        typer.echo("Error: Missing required arguments.", err=True)
        raise typer.Exit(1)
    
    # Use agent for touch operation
    from replx.agent.client import AgentClient
    
    client = AgentClient(port=_get_agent_port())
    success_count = 0
    failed_items = []
    
    for remote in remotes:
        try:
            result = client.send_command('touch', path=remote)
            success_count += 1
            
            if len(remotes) == 1:  # Only show panel for single file
                display_path = result.get('created', remote)
                OutputHelper.print_panel(
                    f"File [bright_blue]{display_path}[/bright_blue] created successfully.",
                    title="Touch File",
                    border_style="green"
                )
        except Exception as e:
            failed_items.append(remote)
            if len(remotes) == 1:  # Only show panel for single file
                OutputHelper.print_panel(
                    f"Touch failed: {e}",
                    title="Touch Failed",
                    border_style="red"
                )
    
    # Summary for multiple files
    if len(remotes) > 1:
        if failed_items:
            OutputHelper.print_panel(
                f"Created [green]{success_count}[/green] file(s).\nFailed: {', '.join(failed_items)}",
                title="Touch Files",
                border_style="yellow"
            )
        else:
            OutputHelper.print_panel(
                f"Created [green]{success_count}[/green] file(s) successfully.",
                title="Touch Files",
                border_style="green"
            )

@app.command()
def ls(
    path: str = typer.Argument("/", help="Directory path to list"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="List subdirectories recursively"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    List the contents of a directory on the connected device.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
List the contents of a directory on the connected device.

[bold cyan]Usage:[/bold cyan]
  replx ls [[cyan]OPTIONS[/cyan]] [yellow][PATH][/yellow]

[bold cyan]Options:[/bold cyan]
  -r, --recursive         List subdirectories recursively

[bold cyan]Arguments:[/bold cyan]
  [yellow]path[/yellow]        Directory path to list [dim][default: /][/dim]

[bold cyan]Examples:[/bold cyan]
  replx ls /lib                      [dim]# List directory[/dim]
  replx ls -r /                      [dim]# List recursively[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    status = _ensure_connected()
    
    # Normalize path
    device_root_fs = status.get('device_root_fs', '/')
    if not path.startswith('/'):
        path = '/' + path

    try:
        with AgentClient(port=_get_agent_port()) as client:
            result = client.send_command('ls', path=path, detailed=True, recursive=recursive)
        
        items = [(item['name'], item['size'], item['is_dir']) for item in result.get('items', [])]
        
        if not items:
            OutputHelper.print_panel(
                f"Directory is empty.",
                title=f"Directory Listing: {path}",
                border_style="dim"
            )
            return
        
        def get_icon(name: str, is_dir: bool) -> str:
            """Get file/folder icon with color"""
            if is_dir:
                return "[#E6B450]󰉋[/#E6B450]"  # folder - gold/yellow
            ext_icons = {
                ".py":   "[#5CB8C2]󰌠[/#5CB8C2]",  # Python - cyan
                ".mpy":  "[#D98C53]󰆧[/#D98C53]",  # compiled - orange
                ".log":  "[#7A7A7A]󰌱[/#7A7A7A]",  # log - gray
                ".ini":  "[#7A7A7A]󰘦[/#7A7A7A]",  # config - gray
            }
            _, ext = os.path.splitext(str(name).lower())
            return ext_icons.get(ext, "[#8C8C8C]󰈙[/#8C8C8C]")  # default - gray

        if recursive:
            # Build tree structure for recursive listing
            from collections import defaultdict
            
            # Build tree dict: path -> list of (basename, size, is_dir, full_path)
            tree = defaultdict(list)
            
            for name, size, is_dir in items:
                # name is full path like /lib/ticle/ext/__init__.mpy
                parent = '/'.join(name.rsplit('/', 1)[:-1]) or '/'
                basename = name.rsplit('/', 1)[-1]
                tree[parent].append((basename, size, is_dir, name))
            
            # Sort items in each directory: folders first, then files, alphabetically
            for parent in tree:
                tree[parent].sort(key=lambda x: (not x[2], x[0].lower()))
            
            # Calculate max size width from original items (3-tuple)
            max_size = max((size for _, size, is_dir in items if not is_dir), default=0)
            size_width = len(str(max_size)) if max_size > 0 else 0
            
            lines = []
            
            def render_tree(dir_path: str, prefix: str = ""):
                """Recursively render tree structure"""
                children = tree.get(dir_path, [])
                for i, (basename, size, is_dir, full_path) in enumerate(children):
                    is_last = (i == len(children) - 1)
                    
                    # Tree branch characters
                    branch = "└── " if is_last else "├── "
                    child_prefix = prefix + ("    " if is_last else "│   ")
                    
                    icon = get_icon(basename, is_dir)
                    
                    if is_dir:
                        name_str = f"[#73B8F1]{basename}[/#73B8F1]"
                        size_str = "".rjust(size_width)
                    else:
                        name_str = basename
                        size_str = str(size).rjust(size_width)
                    
                    lines.append(f"{size_str}  {prefix}{branch}{icon}  {name_str}")
                    
                    # Recurse into directories
                    if is_dir and full_path in tree:
                        render_tree(full_path, child_prefix)
            
            # Start rendering from the listing path
            # First show root folder
            root_icon = get_icon(path, True)
            root_name = f"[#73B8F1]{path}[/#73B8F1]"
            lines.append(f"{''.rjust(size_width)}  {root_icon}  {root_name}")
            
            render_tree(path, "")
            
            OutputHelper.print_panel(
                "\n".join(lines),
                title=f"Directory Tree: {path}",
                border_style="blue"
            )
        else:
            # Non-recursive: simple flat listing
            display_items = []
            for name, size, is_dir in items:
                icon = get_icon(name, is_dir)
                display_items.append((is_dir, name, size, icon))

            if display_items:
                size_width = max(len(str(item[2])) for item in display_items)
                
                lines = []
                for is_dir, f_name, size, icon in display_items:
                    name_str = f"[#73B8F1]{f_name}[/#73B8F1]" if is_dir else f_name
                    size_str = "" if is_dir else str(size)
                    lines.append(f"{size_str.rjust(size_width)}  {icon}  {name_str}")
                
                OutputHelper.print_panel(
                    "\n".join(lines),
                    title=f"Directory Listing: {path}",
                    border_style="blue"
                )

    except ProtocolError:
        OutputHelper.print_panel(
            f"[red]{path[1:]}[/red] does not exist.",
            title=f"Directory Listing: {path}",
            border_style="red"
        )


@app.command()
def put(
    args: Optional[list[str]] = typer.Argument(None, help="Local file(s) and remote destination"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Upload file(s) or directory to the connected device.
    Last argument is the remote destination path.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Upload file(s) or directory to the connected device.
Last argument is the remote destination path.

[bold cyan]Usage:[/bold cyan]
  replx put [yellow]LOCAL... REMOTE[/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]LOCAL...[/yellow]   Local file(s) or directory to upload [red][required][/red]
  [yellow]REMOTE[/yellow]     Remote destination path [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx put ./test.py /lib            [dim]# Upload file to /lib[/dim]
  replx put ./a.py ./b.py /lib        [dim]# Upload multiple files[/dim]
  replx put *.py /backup              [dim]# Upload all .py files[/dim]
  replx put test*.py /lib             [dim]# Upload test*.py files[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    status = _ensure_connected()
    device_root_fs = status.get('device_root_fs', '/')
    
    if not args or len(args) < 2:
        OutputHelper.print_panel(
            "Missing required arguments.\n\n"
            "[bold cyan]Usage:[/bold cyan] replx put [yellow]LOCAL... REMOTE[/yellow]\n\n"
            "At least 2 arguments required: local file(s) and remote destination.",
            title="Upload Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Get raw arguments from sys.argv to avoid Typer's shell expansion
    cmd_idx = next((i for i, arg in enumerate(sys.argv) if arg == 'put'), None)
    if cmd_idx is not None and cmd_idx + 1 < len(sys.argv):
        raw_args = []
        for arg in sys.argv[cmd_idx + 1:]:
            if arg.startswith('-'):
                continue
            raw_args.append(arg)
        if len(raw_args) >= 2:
            args = raw_args
    
    # Last argument is remote destination
    remote = args[-1]
    locals = args[:-1]
    
    # Normalize remote path
    if not remote.startswith('/'):
        remote = '/' + remote
    
    # Expand wildcards and collect all files to upload
    files_to_upload = []
    
    for local_pattern in locals:
        # Expand wildcards
        if '*' in local_pattern or '?' in local_pattern:
            matched_files = glob.glob(local_pattern)
            if not matched_files:
                OutputHelper.print_panel(
                    f"[red]{local_pattern}[/red] - pattern did not match any files.",
                    title="Upload Failed",
                    border_style="red"
                )
                continue
            for matched in matched_files:
                if os.path.exists(matched):
                    files_to_upload.append(matched)
        else:
            if not os.path.exists(local_pattern):
                OutputHelper.print_panel(
                    f"[red]{local_pattern}[/red] does not exist.",
                    title="Upload Failed",
                    border_style="red"
                )
                continue
            files_to_upload.append(local_pattern)
    
    if not files_to_upload:
        OutputHelper.print_panel(
            "No files to upload.",
            title="Upload",
            border_style="yellow"
        )
        raise typer.Exit(1)
    
    client = AgentClient(port=_get_agent_port())
    
    # Check if remote destination is a directory
    try:
        result = client.send_command('is_dir', path=remote)
        is_remote_dir = result.get('is_dir', False)
    except Exception:
        # Remote doesn't exist - will be created if needed
        is_remote_dir = remote.endswith('/')
    
    # Upload files
    total_files = len(files_to_upload)
    success_count = 0
    
    if total_files == 1:
        # Single file/directory - use original behavior
        local = files_to_upload[0]
        is_dir = os.path.isdir(local)
        base_name = os.path.basename(local)
        
        # Determine remote destination
        if is_remote_dir:
            remote_path = posixpath.join(remote, base_name)
        else:
            remote_path = remote
        
        display_remote = remote_path.replace(device_root_fs, "", 1)
        item_type = "Directory" if is_dir else "File"
        
        # Count files for progress (for directories)
        if is_dir:
            file_count = sum(1 for _, _, files in os.walk(local) for _ in files)
        else:
            file_count = 1
            file_size = os.path.getsize(local)
        
        # Progress state for streaming updates
        progress_state = {"current": 0, "total": file_count, "file": base_name}
        
        def progress_callback(data):
            """Handle streaming progress updates."""
            progress_state["current"] = data.get("current", 0)
            progress_state["total"] = data.get("total", file_count)
            progress_state["file"] = data.get("file", base_name)
        
        try:
            with Live(OutputHelper.create_progress_panel(0, file_count, title=f"Uploading {base_name}", message=f"Uploading {item_type.lower()}..."), console=OutputHelper._console, refresh_per_second=10) as live:
                # Start upload in background with streaming
                import threading
                upload_error = [None]
                upload_result = [None]
                
                def do_upload():
                    try:
                        if is_dir:
                            upload_result[0] = client.send_command_streaming(
                                'putdir_from_local_streaming',
                                local_path=local,
                                remote_path=remote_path,
                                timeout=300,
                                progress_callback=progress_callback
                            )
                        else:
                            upload_result[0] = client.send_command_streaming(
                                'put_from_local_streaming',
                                local_path=local,
                                remote_path=remote_path,
                                timeout=60,
                                progress_callback=progress_callback
                            )
                    except Exception as e:
                        upload_error[0] = e
                
                upload_thread = threading.Thread(target=do_upload, daemon=True)
                upload_thread.start()
                
                # Update progress bar while upload is running
                while upload_thread.is_alive():
                    if is_dir:
                        # Directory: show file count progress
                        live.update(OutputHelper.create_progress_panel(
                            progress_state["current"],
                            progress_state["total"],
                            title=f"Uploading {base_name}",
                            message=f"Uploading {progress_state['file']}..."
                        ))
                    else:
                        # Single file: show byte progress
                        live.update(OutputHelper.create_progress_panel(
                            progress_state["current"],
                            progress_state["total"],
                            title=f"Uploading {base_name}",
                            message=f"Uploading file..."
                        ))
                    time.sleep(0.1)
                
                upload_thread.join()
                
                if upload_error[0]:
                    raise upload_error[0]
                
                # Final update
                live.update(OutputHelper.create_progress_panel(
                    progress_state["total"],
                    progress_state["total"],
                    title=f"Uploading {base_name}"
                ))
            
            OutputHelper.print_panel(
                f"Uploaded [green]{local}[/green]\nto [bright_blue]{display_remote}[/bright_blue]",
                title="Upload Complete",
                border_style="green"
            )
        except Exception as e:
            OutputHelper.print_panel(
                f"Upload failed: [red]{str(e)}[/red]",
                title="Upload Failed",
                border_style="red"
            )
            raise typer.Exit(1)
    else:
        # Multiple files - remote must be a directory
        if not is_remote_dir:
            OutputHelper.print_panel(
                f"Destination [red]{remote}[/red] must be a directory when uploading multiple files.",
                title="Upload Failed",
                border_style="red"
            )
            raise typer.Exit(1)
        
        # Progress state for streaming updates
        current_file_progress = {"file": "", "current": 0, "total": 0}
        
        def progress_callback(data):
            """Handle streaming progress updates for current file."""
            current_file_progress["file"] = data.get("file", "")
            current_file_progress["current"] = data.get("current", 0)
            current_file_progress["total"] = data.get("total", 0)
        
        with Live(OutputHelper.create_progress_panel(0, total_files, title=f"Uploading {total_files} file(s)", message="Starting..."), console=OutputHelper._console, refresh_per_second=10) as live:
            for idx, local in enumerate(files_to_upload):
                base_name = os.path.basename(local)
                is_dir = os.path.isdir(local)
                remote_path = posixpath.join(remote, base_name)
                
                # Reset current file progress
                current_file_progress["file"] = base_name
                current_file_progress["current"] = 0
                current_file_progress["total"] = 0
                
                try:
                    # Use streaming for real-time progress
                    if is_dir:
                        result = client.send_command_streaming(
                            'putdir_from_local_streaming',
                            local_path=local,
                            remote_path=remote_path,
                            timeout=300,
                            progress_callback=progress_callback
                        )
                    else:
                        result = client.send_command_streaming(
                            'put_from_local_streaming',
                            local_path=local,
                            remote_path=remote_path,
                            timeout=60,
                            progress_callback=progress_callback
                        )
                    success_count += 1
                    live.update(OutputHelper.create_progress_panel(
                        idx + 1, total_files,
                        title=f"Uploading {total_files} file(s)",
                        message=f"Completed {base_name}"
                    ))
                except Exception as e:
                    OutputHelper._console.print(f"[red]Failed to upload {base_name}: {str(e)}[/red]")
            
            live.update(OutputHelper.create_progress_panel(total_files, total_files, title=f"Uploading {total_files} file(s)"))
        
        display_remote = remote.replace(device_root_fs, "", 1)
        OutputHelper.print_panel(
            f"Uploaded [green]{success_count}[/green] out of {total_files} file(s)\nto [bright_blue]{display_remote}[/bright_blue]",
            title="Upload Complete",
            border_style="green" if success_count == total_files else "yellow"
        )


@app.command()
def run(
    script_file: str = typer.Argument("", help="Script file to run"),
    non_interactive: bool = typer.Option(False, "--non-interactive", "-n", help="Non-interactive execution"),
    echo: bool = typer.Option(False, "--echo", "-e", help="Turn on echo for interactive"),
    device: bool = typer.Option(False, "--device", "-d", help="Run from device storage"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Run a script on the connected device.
    By default, runs a local file. Use -d to run from device storage.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Run a script on the connected device.
By default, runs a local file. Use -d to run from device storage.

[bold cyan]Usage:[/bold cyan]
  replx run [[cyan]OPTIONS[/cyan]] [yellow]SCRIPT_FILE[/yellow]

[bold cyan]Options:[/bold cyan]
  -n, --non-interactive   Non-interactive execution (detach)
  -e, --echo              Turn on echo for interactive
  -d, --device            Run from device storage (not local)

[bold cyan]Arguments:[/bold cyan]
  [yellow]script_file[/yellow]  Script file to run [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  replx run ./test.py                [dim]# Run local script[/dim]
  replx run test.py                  [dim]# Run local script[/dim]
  replx run -n ./test.py             [dim]# Run without interaction (detach)[/dim]
  replx run -d boo.py                [dim]# Run /boo.py from device[/dim]
  replx run -d /lib/main.py          [dim]# Run /lib/main.py from device[/dim]
  replx run -dn main.py              [dim]# Run from device, detached[/dim]
  replx run -de main.py              [dim]# Run from device with echo[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    from ..agent.client import AgentClient
    
    if not script_file:
        typer.echo("Error: Missing required argument 'SCRIPT_FILE'.", err=True)
        raise typer.Exit(1)
    
    if non_interactive and echo:
        typer.echo("Error: The --non-interactive and --echo options cannot be used together.", err=True)
        raise typer.Exit(1)
    
    _ensure_connected()
    
    client = AgentClient(port=_get_agent_port())
    
    local_file = None
    remote_path = None
    device_exec_code = None
    
    if device:
        if script_file.startswith('/'):
            remote_path = script_file
        else:
            remote_path = '/' + script_file
        
        # Check if file exists on device before attempting to run
        try:
            with AgentClient(port=_get_agent_port()) as check_client:
                check_code = f"import os; print(os.stat('{remote_path}')[0])"
                result = check_client.send_command('exec', code=check_code)
                output = result.get('output', '').strip()
                # If output is empty or contains error, file doesn't exist
                if not output or 'Error' in result.get('error', ''):
                    raise FileNotFoundError()
        except Exception:
            OutputHelper.print_panel(
                f"File not found on device: [red]{remote_path}[/red]",
                title="File Not Found",
                border_style="red"
            )
            raise typer.Exit(1)
        
        # Generate exec command for device file
        # .mpy files need special handling - clear from sys.modules first to ensure fresh execution
        if remote_path.endswith('.mpy'):
            # Extract module name from path: /lib/t1.mpy -> lib.t1 or /t1.mpy -> t1
            mod_path = remote_path[1:-4]  # Remove leading / and .mpy
            mod_name = mod_path.replace('/', '.')
            # For lib/xxx, we need to import just xxx since lib is in sys.path
            if mod_name.startswith('lib.'):
                mod_name = mod_name[4:]  # Remove 'lib.' prefix
            # Remove from sys.modules first to ensure fresh import each time
            device_exec_code = f"import sys; sys.modules.pop('{mod_name}', None); import {mod_name}"
        else:
            device_exec_code = f"exec(open('{remote_path}').read())"
    else:
        # Local mode: run local file (must exist)
        if not os.path.exists(script_file):
            OutputHelper.print_panel(
                f"File not found: [red]{script_file}[/red]\n\n"
                "Use [bright_blue]-d[/bright_blue] option to run from device storage.",
                title="File Not Found",
                border_style="red"
            )
            raise typer.Exit(1)
        local_file = script_file
    
    if not non_interactive:
        # Interactive mode: use streaming execution via agent
        stop_requested = False
        ctrl_c_count = 0  # Track consecutive Ctrl+C presses
        pending_input = []  # Queue for input from signal handler
        stderr_buffer = bytearray()  # Collect stderr for error display
        
        # Platform-specific terminal setup
        if not IS_WINDOWS:
            import tty
            import termios
            old_settings = None
            fd = sys.stdin.fileno()
            try:
                old_settings = termios.tcgetattr(fd)
            except Exception:
                pass
        
        def output_callback(data: bytes, stream_type: str = "stdout"):
            """Handle streaming output from device."""
            nonlocal ctrl_c_count, stderr_buffer
            # Reset Ctrl+C count when we receive output (script is responding)
            ctrl_c_count = 0
            try:
                if stream_type == "stderr":
                    # Collect stderr for error display
                    stderr_buffer.extend(data)
                else:
                    # stdout goes directly to terminal
                    # Remove \r to avoid double line feeds on Windows
                    if IS_WINDOWS:
                        data = data.replace(b'\r', b'')
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
            except Exception:
                pass
        
        def input_provider() -> bytes:
            """Provide keyboard input to device."""
            nonlocal ctrl_c_count, stop_requested, pending_input
            
            # First check pending input from signal handler
            if pending_input:
                return pending_input.pop(0)
            
            try:
                if IS_WINDOWS:
                    import msvcrt
                    if msvcrt.kbhit():
                        ch = msvcrt.getwch()
                        if ch == '\x03':  # Ctrl+C
                            ctrl_c_count += 1
                            if ctrl_c_count >= 2:
                                # Double Ctrl+C: force stop
                                stop_requested = True
                                return None
                            # Single Ctrl+C: send to device
                            return b'\x03'
                        elif ch == '\x04':  # Ctrl+D
                            return b'\x04'
                        elif ch == '\r':  # Enter key
                            if echo:
                                sys.stdout.write('\r\n')
                                sys.stdout.flush()
                            return b'\r'
                        elif ch == '\n':  # Also map newline to CR
                            if echo:
                                sys.stdout.write('\r\n')
                                sys.stdout.flush()
                            return b'\r'
                        elif ch == '\x08':  # Backspace
                            if echo:
                                # Erase character: move back, overwrite with space, move back
                                sys.stdout.write('\b \b')
                                sys.stdout.flush()
                            return b'\x08'
                        elif ch in ('\x00', '\xe0'):  # Extended key
                            ext = msvcrt.getwch()
                            # Map arrow keys etc.
                            ext_map = {
                                'H': b'\x1b[A',  # Up
                                'P': b'\x1b[B',  # Down
                                'M': b'\x1b[C',  # Right
                                'K': b'\x1b[D',  # Left
                            }
                            return ext_map.get(ext, b'')
                        else:
                            ctrl_c_count = 0  # Reset on other keys
                            if echo:
                                sys.stdout.write(ch)
                                sys.stdout.flush()
                            return ch.encode('utf-8')
                else:
                    # Unix/Linux/macOS - use select for non-blocking read
                    import select
                    r, _, _ = select.select([sys.stdin], [], [], 0)
                    if r:
                        ch = os.read(sys.stdin.fileno(), 1)
                        if ch == b'\x03':  # Ctrl+C
                            ctrl_c_count += 1
                            if ctrl_c_count >= 2:
                                stop_requested = True
                                return None
                            return b'\x03'  # Send to device
                        elif ch == b'\n':  # Enter key on Unix
                            ctrl_c_count = 0
                            if echo:
                                sys.stdout.buffer.write(b'\r\n')
                                sys.stdout.buffer.flush()
                            return b'\r'
                        else:
                            ctrl_c_count = 0
                            if echo:
                                sys.stdout.buffer.write(ch)
                                sys.stdout.buffer.flush()
                        return ch
            except Exception:
                pass
            return None
        
        def stop_check() -> bool:
            """Check if stop was requested."""
            return stop_requested
        
        # Suppress KeyboardInterrupt during interactive mode
        original_sigint = signal.getsignal(signal.SIGINT)
        
        def sigint_handler(signum, frame):
            """Handle SIGINT by queuing Ctrl+C to send to device."""
            nonlocal ctrl_c_count, stop_requested, pending_input
            ctrl_c_count += 1
            if ctrl_c_count >= 2:
                stop_requested = True
            else:
                # Queue Ctrl+C to be sent to device
                pending_input.append(b'\x03')
        
        try:
            # Set up signal handler
            signal.signal(signal.SIGINT, sigint_handler)
            
            # Set terminal to raw mode on Unix for proper key handling
            if not IS_WINDOWS and old_settings is not None:
                try:
                    tty.setraw(fd)
                except Exception:
                    pass
            
            # Device mode: send exec command, Local mode: send file content
            try:
                if device_exec_code:
                    result = client.run_interactive(
                        script_content=device_exec_code,
                        echo=echo,
                        output_callback=output_callback,
                        input_provider=input_provider,
                        stop_check=stop_check
                    )
                else:
                    result = client.run_interactive(
                        script_path=local_file,
                        echo=echo,
                        output_callback=output_callback,
                        input_provider=input_provider,
                        stop_check=stop_check
                    )
            except KeyboardInterrupt:
                # Caught here first - signal handler might not catch it
                stop_requested = True
                try:
                    client.send_command('run_stop', timeout=0.3)
                except Exception:
                    pass
                print("\n[Interrupted]")
                return
            
            # Print newline after execution
            print()
            
            # Display stderr as error panel if present
            if stderr_buffer:
                stderr_text = stderr_buffer.decode('utf-8', errors='replace').strip()
                if stderr_text:
                    # Convert traceback file references to clickable links
                    # VSCode terminal recognizes "path:line" format as clickable
                    import re
                    script_abs_path = os.path.abspath(local_file) if local_file else None
                    
                    def make_file_link(match):
                        """Convert File "<stdin>", line X to clickable path:line format."""
                        file_ref = match.group(1)  # e.g., "<stdin>" or "/lib/foo.py"
                        line_num = match.group(2)
                        
                        if file_ref == "<stdin>":
                            # <stdin> means the script we ran
                            if script_abs_path:
                                return f'File "{script_abs_path}", line {line_num}'
                            else:
                                return match.group(0)  # Keep original
                        else:
                            # Other files - look in ~/.replx/
                            # e.g., "/lib/ticle/motor.py" -> ~/.replx/device/ticle/src/ticle/motor.py
                            replx_home = StoreManager.home_store()
                            possible_paths = [
                                os.path.join(replx_home, "core", STATE.core or "", "src", file_ref.lstrip('/')),
                                os.path.join(replx_home, "device", STATE.device or "", "src", file_ref.lstrip('/')),
                            ]
                            for path in possible_paths:
                                if os.path.exists(path):
                                    return f'File "{path}", line {line_num}'
                            return match.group(0)  # Keep original if not found
                    
                    # Pattern: File "...", line X
                    linked_text = re.sub(
                        r'File "([^"]+)", line (\d+)',
                        make_file_link,
                        stderr_text
                    )
                    
                    OutputHelper.print_panel(
                        linked_text,
                        title="Execution Error",
                        border_style="red"
                    )
            
        except KeyboardInterrupt:
            # This shouldn't happen with our handler, but just in case
            stop_requested = True
            try:
                client.send_command('run_stop', timeout=0.1)
            except Exception:
                pass
            print("\n[Interrupted by user]")
        except Exception as e:
            error_msg = str(e)
            if 'Not connected' in error_msg:
                OutputHelper.print_panel(
                    "Not connected to any device.\n\nRun [bright_green]replx connect --port COM3[/bright_green] first.",
                    title="Connection Required",
                    border_style="red"
                )
            else:
                OutputHelper.print_panel(
                    f"Error: {str(e)}",
                    title="Execution Failed",
                    border_style="red"
                )
            raise typer.Exit(1)
        finally:
            # Restore original SIGINT handler
            signal.signal(signal.SIGINT, original_sigint)
            
            # Restore terminal settings on Unix
            if not IS_WINDOWS and old_settings is not None:
                try:
                    import termios
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass
        
        return
    
    # Non-interactive mode: send script and exit immediately
    try:
        # Device mode: send exec command, Local mode: send file content
        if device_exec_code:
            result = client.send_command('run', script_content=device_exec_code, detach=True)
        else:
            result = client.send_command('run', script_path=local_file, detach=True)
        
        display_name = remote_path if remote_path else local_file
        OutputHelper.print_panel(
            f"Script [bright_blue]{display_name}[/bright_blue] sent to device.\n\n"
            "[yellow]⚠ Detached mode:[/yellow] Device may still be executing.\n"
            "Other commands may fail until script completes.",
            title="Script Sent",
            border_style="green"
        )
    except Exception as e:
        error_msg = str(e)
        if 'Not connected' in error_msg:
            OutputHelper.print_panel(
                "Not connected to any device.\n\nRun [bright_green]replx connect --port COM3[/bright_green] first.",
                title="Connection Required",
                border_style="red"
            )
        else:
            OutputHelper.format_error_output(error_msg.strip().split('\n'), local_file if local_file else script_file)
        raise typer.Exit(1)


@app.command()
def repl(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Enter the REPL (Read-Eval-Print Loop) mode.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Enter the REPL (Read-Eval-Print Loop) mode for interactive device control.

[bold cyan]Usage:[/bold cyan]
  replx repl

[bold cyan]Examples:[/bold cyan]
  replx repl                         [dim]# Enter REPL mode[/dim]
  [dim]# Type commands interactively, type 'exit' and press Enter to exit[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    status = _ensure_connected()
    
    from ..agent.client import AgentClient
    import threading
    import sys
    
    port = status.get('port')
    if not port:
        OutputHelper.print_panel(
            "Could not determine port from agent status.",
            title="REPL Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    # Enter Friendly REPL mode via agent
    initial_output = ""
    try:
        with AgentClient(port=_get_agent_port()) as client:
            result = client.send_command('repl_enter')
            if result.get('error'):
                error_msg = result.get('error', 'Unknown error')
                OutputHelper.print_panel(
                    f"Failed to enter Friendly REPL.\n{error_msg}",
                    title="REPL Error",
                    border_style="red"
                )
                raise typer.Exit(1)
            if not result.get('entered'):
                OutputHelper.print_panel(
                    "Failed to enter Friendly REPL.\nNo prompt received from device.",
                    title="REPL Error",
                    border_style="red"
                )
                raise typer.Exit(1)
            # Store initial output (contains prompt)
            initial_output = result.get('output', '')
    except typer.Exit:
        raise  # Re-raise typer.Exit without catching
    except Exception as e:
        OutputHelper.print_panel(
            f"Failed to enter Friendly REPL.\nError: {e}",
            title="REPL Error",
            border_style="red"
        )
        raise typer.Exit(1)
    
    OutputHelper.print_panel(
        f"Connected to [bright_yellow]{STATE.device}[/bright_yellow] on [bright_green]{STATE.core}[/bright_green]\n"
        f"Type [cyan]exit[/cyan] and press Enter to exit REPL mode.",
        title="REPL Mode",
        border_style="magenta"
    )
    
    # ANSI color for yellow prompt
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    
    def colorize_prompt(text: str) -> str:
        """Colorize >>> and ... prompts to yellow."""
        # Replace >>> and ... at line start with yellow version
        import re
        text = re.sub(r'^(>>>|\.\.\.)', f'{YELLOW}\\1{RESET}', text, flags=re.MULTILINE)
        return text
    
    # Print initial prompt with color
    if initial_output:
        print(colorize_prompt(initial_output), end="", flush=True)
    
    # Flag for reader thread
    repl_running = [True]
    # Shared client for reader thread (reduces connection overhead)
    reader_client = [None]
    
    def reader_thread_func():
        """Background thread that reads agent output and prints to stdout."""
        try:
            reader_client[0] = AgentClient(port=_get_agent_port())
            while repl_running[0]:
                try:
                    result = reader_client[0].send_command('repl_read')
                    output = result.get('output', '')
                    if output:
                        # Colorize prompt
                        output = colorize_prompt(output)
                        if IS_WINDOWS:
                            sys.stdout.buffer.write(output.encode('utf-8').replace(b'\r', b''))
                        else:
                            sys.stdout.buffer.write(output.encode('utf-8'))
                        sys.stdout.buffer.flush()
                except:
                    if not repl_running[0]:
                        break
                    time.sleep(0.05)
                time.sleep(0.005)  # 5ms polling
        finally:
            if reader_client[0]:
                try:
                    reader_client[0].__exit__(None, None, None)
                except:
                    pass
    
    # Start reader thread
    reader = threading.Thread(target=reader_thread_func, daemon=True, name='REPL-Output')
    reader.start()
    
    # Shared client for writer (reduces connection overhead)
    writer_client = AgentClient(port=_get_agent_port())
    
    # Input buffer for exit detection
    input_buffer = ""
    
    # Main loop: read keyboard and send to device
    try:
        while True:
            char = getch()
            
            if char == b'\x00' or not char:
                continue
            
            # Ctrl+D exits immediately
            if char == b'\x04':
                break
            
            # Track input for 'exit' detection
            if char in (b'\r', b'\n'):
                # Check if user typed 'exit' - send Ctrl+C to cancel, then exit cleanly
                if input_buffer.strip().lower() in ('exit', 'exit()'):
                    # Send Ctrl+C to cancel the 'exit' command on device
                    try:
                        writer_client.send_command('repl_write', data='\x03')
                    except:
                        pass
                    time.sleep(0.05)
                    break
                input_buffer = ""
                # Send Enter to device
                try:
                    writer_client.send_command('repl_write', data='\r')
                except:
                    break
            elif char == b'\x7f' or char == b'\x08':  # Backspace
                if input_buffer:
                    input_buffer = input_buffer[:-1]
                # Send backspace to device
                try:
                    writer_client.send_command('repl_write', data=char.decode('utf-8', errors='replace'))
                except:
                    break
            else:
                # Accumulate printable characters for exit detection
                if char >= b' ':
                    try:
                        input_buffer += char.decode('utf-8', errors='ignore')
                    except:
                        pass
                # Send character to device
                try:
                    writer_client.send_command('repl_write', data=char.decode('utf-8', errors='replace'))
                except:
                    break
                
    except KeyboardInterrupt:
        pass
    finally:
        # Stop reader thread
        repl_running[0] = False
        reader.join(timeout=0.5)
        
        # Close writer client
        try:
            writer_client.__exit__(None, None, None)
        except:
            pass
        
        # Exit REPL session on agent
        try:
            with AgentClient(port=_get_agent_port()) as client:
                client.send_command('repl_exit')
        except:
            pass
    
    print()


_is_stop_spinner = None

@app.command()
def format(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Format the file system of the connected device.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Format the file system of the connected device.

[bold cyan]Usage:[/bold cyan]
  replx format

[bold cyan]Examples:[/bold cyan]
  replx format                       [dim]# Format device filesystem[/dim]
  [dim]# Warning: This will erase all files on the device[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    global _is_stop_spinner

    _is_stop_spinner = False
    frame_idx = [0]
    
    def _spinner_task(live):
        """Spinner runs in thread to show progress"""
        try:
            while not _is_stop_spinner:
                live.update(OutputHelper.create_spinner_panel(
                    f"Formatting file system on {STATE.device}...",
                    title="Format File System",
                    frame_idx=frame_idx[0]
                ))
                frame_idx[0] += 1
                time.sleep(0.1)
        except Exception:
            pass
    
    ret = None
    error = None
    
    try:
        with Live(OutputHelper.create_spinner_panel(
            f"Formatting file system on {STATE.device}...",
            title="Format File System",
            frame_idx=0
        ), console=OutputHelper._console, refresh_per_second=10) as live:
            # Start spinner thread
            spinner_thread = threading.Thread(target=_spinner_task, args=(live,), daemon=True)
            spinner_thread.start()
            
            # Execute format using agent
            try:
                from replx.agent.client import AgentClient
                client = AgentClient(port=_get_agent_port())
                result = client.send_command('format')
                # send_command returns result dict directly, raises on error
                ret = result.get('formatted', True)
            except Exception as e:
                error = e
            finally:
                # Stop spinner
                _is_stop_spinner = True
                spinner_thread.join(timeout=1.0)
    
    except KeyboardInterrupt:
        _is_stop_spinner = True
        OutputHelper.print_panel(
            "Format operation cancelled by user.",
            title="Format Cancelled",
            border_style="red"
        )
        return False
    
    if error:
        OutputHelper.print_panel(
            f"Format failed: [red]{error}[/red]",
            title="Format Failed",
            border_style="red"
        )
        return False
    
    if ret:
        # Free agent connection after format for EFR32MG (XBee3)
        # EFR32MG's os.format() resets the device, invalidating the connection
        # Other cores (RP2350, etc.) don't reset on format
        if STATE.core == 'EFR32MG':
            try:
                from replx.agent.client import AgentClient
                client = AgentClient(port=_get_agent_port())
                client.send_command('free')
            except Exception:
                pass  # Ignore errors - agent may already be gone
        
        OutputHelper.print_panel(
            f"File system on [bright_yellow]{STATE.device}[/bright_yellow] has been formatted successfully.",
            title="Format Complete",
            border_style="green"
        )
    else:
        OutputHelper.print_panel(
            f"Device [red]{STATE.device}[/red] does not support formatting.",
            title="Format Failed",
            border_style="red"
        )
    return ret

@app.command()
def init(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Initialize the device by formatting and installing libraries.
    
    This command combines 'format' and 'install' operations:
    1. Format the device file system
    2. Install core and device libraries
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Initialize the device by formatting and installing libraries.

This command combines 'format' and 'install' operations:
1. Format the device file system
2. Install core and device libraries

[bold cyan]Usage:[/bold cyan]
  replx init

[bold cyan]Examples:[/bold cyan]
  replx init                         [dim]# Initialize device[/dim]
  [dim]# Warning: This will erase all files and reinstall libs[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    # Step 1: Format the device
    OutputHelper.print_panel(
        "Step 1/2: Formatting device file system...",
        title="Device Initialization",
        border_style="cyan"
    )
    
    try:
        from replx.agent.client import AgentClient
        client = AgentClient(port=_get_agent_port())
        result = client.send_command('format')
        # send_command returns result dict directly, raises on error
        format_result = result.get('formatted', True)
        if not format_result:
            OutputHelper.print_panel(
                "Initialization failed: Format operation was unsuccessful.",
                title="Initialization Failed",
                border_style="red"
            )
            return False
    except Exception as e:
        OutputHelper.print_panel(
            f"Format failed: [red]{e}[/red]",
            title="Format Failed",
            border_style="red"
        )
        return False
    
    # Success message for format step
    OutputHelper.print_panel(
        f"File system on [bright_yellow]{STATE.device}[/bright_yellow] has been formatted successfully.",
        title="Format Complete",
        border_style="green"
    )
    
    # Reconnect agent after format to ensure fresh filesystem state
    try:
        # Resolve connection using new multi-device system
        conn = _resolve_connection()
        if not conn:
            raise RuntimeError("No connection configuration found")
        
        agent_port = conn.get('agent_port', DEFAULT_AGENT_PORT)
        port = conn['connection'] if conn['is_serial'] else None
        target = None
        if not conn['is_serial']:
            if conn.get('password'):
                target = f"{conn['connection']}:{conn['password']}"
            else:
                target = conn['connection']
        core = conn.get('core') or STATE.core
        device = conn.get('device') or STATE.device
        
        client = AgentClient(port=agent_port)
        
        # Free current connection - this will shutdown the agent
        try:
            client.send_command('free')
        except Exception:
            pass  # Agent may already be gone
        
        import time
        time.sleep(0.5)  # Wait for port to be released
        
        # Start new agent and reconnect
        AgentClient.start_agent(port=agent_port)
        time.sleep(0.3)  # Wait for agent to start
        
        client = AgentClient(port=agent_port)
        resp = client.send_command('connect', port=port, target=target, core=core, device=device)
        if not resp.get('connected'):
            raise RuntimeError(f"Reconnect failed: {resp}")
        
        # Update session file
        _write_session(conn['connection'], agent_port)
    except Exception as e:
        OutputHelper.print_panel(
            f"Failed to reconnect after format: [red]{e}[/red]",
            title="Reconnect Failed",
            border_style="red"
        )
        return False
    
    # Step 2: Install libraries
    OutputHelper.print_panel(
        "Step 2/2: Installing libraries to device...",
        title="Device Initialization",
        border_style="cyan"
    )
    
    try:
        # Install core and device libraries without re-entering CLI callback
        StoreManager.ensure_home_store()
        
        # Check if meta file exists (required for any installation)
        meta_path = StoreManager.local_meta_path()
        if not os.path.isfile(meta_path):
            raise typer.BadParameter(
                "Local store is not ready. Please run 'replx update' first. (meta missing)"
            )
        
        # Check core - required
        core_src = os.path.join(StoreManager.pkg_root(), "core", STATE.core, "src")
        if not os.path.isdir(core_src):
            raise typer.BadParameter(
                f"Core library for {STATE.core} not found. Please run 'replx update' first."
            )
        
        # Prepare install specs
        specs_to_install = ["core/"]
        
        # Check device - optional
        dev_src = os.path.join(StoreManager.pkg_root(), "device", STATE.device, "src")
        if os.path.isdir(dev_src):
            specs_to_install.append("device/")
        
        # Install available specs in sequence
        for spec_item in specs_to_install:
            _install_spec_internal(spec_item)
    except Exception as e:
        OutputHelper.print_panel(
            f"Initialization failed during install: [red]{e}[/red]",
            title="Initialization Failed",
            border_style="red"
        )
        return False
    
    # Free agent connection after init for EFR32MG (XBee3)
    # EFR32MG's os.format() resets the device, invalidating the connection
    # Other cores (RP2350, etc.) don't reset on format
    if STATE.core == 'EFR32MG':
        try:
            from replx.agent.client import AgentClient
            client = AgentClient(port=_get_agent_port())
            client.send_command('free')
        except Exception:
            pass  # Ignore errors - agent may already be gone
    
    # Success message
    OutputHelper.print_panel(
        f"Device [bright_yellow]{STATE.device}[/bright_yellow] has been initialized successfully.\n"
        "The device is now ready to use.",
        title="Initialization Complete",
        border_style="green"
    )
    return True

@app.command()
def shell(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Enter an interactive shell for device control.
    Provides a shell-like environment where you can run replx commands without the 'replx' prefix.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Enter an interactive shell for device control.
Commands run as if you typed 'replx <command>' but without the 'replx' prefix.

[bold cyan]Usage:[/bold cyan]
  replx shell

[bold cyan]Available Commands:[/bold cyan]
  [yellow]ls[/yellow]       List files/directories (replx ls)
  [yellow]cat[/yellow]      Display file contents (replx cat)
  [yellow]cp[/yellow]       Copy files (replx cp)
  [yellow]mv[/yellow]       Move/rename files (replx mv)
  [yellow]rm[/yellow]       Remove files (replx rm)
  [yellow]mkdir[/yellow]    Create directories (replx mkdir)
  [yellow]touch[/yellow]    Create empty files (replx touch)
  [yellow]info[/yellow]     Show device info (replx info)
  [yellow]exec[/yellow]     Execute Python code (replx exec)
  [yellow]repl[/yellow]     Enter Python REPL (replx repl)
  [yellow]run[/yellow]      Run script from device (replx run -d)

[bold cyan]Shell-only Commands:[/bold cyan]
  [yellow]cd[/yellow]       Change current directory
  [yellow]pwd[/yellow]      Print current directory
  [yellow]clear[/yellow]    Clear screen
  [yellow]edit[/yellow]     Edit file in VSCode
  [yellow]exit[/yellow]     Exit shell

[bold cyan]Examples:[/bold cyan]
  replx shell                 [dim]# Enter shell mode[/dim]
  [dim]> ls /lib[/dim]               [dim]# = replx ls /lib[/dim]
  [dim]> cat main.py[/dim]           [dim]# = replx cat main.py[/dim]
  [dim]> run t1.py[/dim]             [dim]# = replx run -d t1.py[/dim]
  [dim]> cp *.py backup/[/dim]       [dim]# = replx cp *.py backup/[/dim]
  [dim]> exec "print(1+2)"[/dim]     [dim]# = replx exec "print(1+2)"[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()
    
    # Commands available in shell mode
    SHELL_COMMANDS = {
        'ls', 'cat', 'cp', 'mv', 'rm', 'mkdir', 'touch', 'info', 'exec', 'repl', 'run',
        'cd', 'pwd', 'clear', 'edit', 'exit', 'help', '?'
    }
    
    # Commands not available in shell (these require PC-side operations)
    EXCLUDED_COMMANDS = {
        'version', 'setup', 'scan', 'shell', 'reset', 'get', 'put', 'format', 
        'init', 'install', 'update', 'search'
    }
    
    current_path = '/'
    
    def print_prompt():
        print(f"\n[{STATE.device}]:{current_path} > ", end="", flush=True)

    def print_shell_help(cmd: str):
        """Print help for a shell command by calling the corresponding replx command with --help."""
        from rich.panel import Panel
        shell_console = Console(width=CONSOLE_WIDTH)
        
        # Shell-specific commands
        shell_only_help = {
            "cd": """\
[bold cyan]Usage:[/bold cyan]
  cd [yellow]DIRECTORY[/yellow]

[bold cyan]Description:[/bold cyan]
  Change current working directory

[bold cyan]Examples:[/bold cyan]
  cd /lib      [dim]# Change to /lib[/dim]
  cd ..        [dim]# Go to parent directory[/dim]
  cd subdir    [dim]# Enter subdirectory[/dim]""",
            
            "pwd": """\
[bold cyan]Usage:[/bold cyan]
  pwd

[bold cyan]Description:[/bold cyan]
  Print current working directory""",
            
            "clear": """\
[bold cyan]Usage:[/bold cyan]
  clear

[bold cyan]Description:[/bold cyan]
  Clear the terminal screen""",
            
            "exit": """\
[bold cyan]Usage:[/bold cyan]
  exit

[bold cyan]Description:[/bold cyan]
  Exit the shell and return to normal terminal""",
            
            "edit": """\
[bold cyan]Usage:[/bold cyan]
  edit [yellow]FILE[/yellow]

[bold cyan]Description:[/bold cyan]
  Edit a file from device in VSCode
  - Downloads file to .temp folder
  - Opens in VSCode and waits for close
  - Prompts to upload if file was modified

[bold cyan]Examples:[/bold cyan]
  edit main.py        [dim]# Edit main.py[/dim]
  edit /lib/utils.py  [dim]# Edit with absolute path[/dim]""",
            
            "help": """\
[bold cyan]Usage:[/bold cyan]
  help [yellow][COMMAND][/yellow]
  ? [yellow][COMMAND][/yellow]

[bold cyan]Description:[/bold cyan]
  Show help information

[bold cyan]Examples:[/bold cyan]
  help       [dim]# Show all commands[/dim]
  help ls    [dim]# Show help for ls command[/dim]""",
        }
        shell_only_help["?"] = shell_only_help["help"]
        
        if cmd in shell_only_help:
            shell_console.print(Panel(shell_only_help[cmd], border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
            return
        
        # For replx commands, call with show_help=True
        # Note: help text will show "replx" prefix, user knows it's omitted in shell
        try:
            if cmd == "ls":
                ls(path="/", recursive=False, show_help=True)
            elif cmd == "cat":
                cat(remote="", encoding="utf-8", show_help=True)
            elif cmd == "cp":
                cp(args=None, recursive=False, show_help=True)
            elif cmd == "mv":
                mv(args=None, recursive=False, show_help=True)
            elif cmd == "rm":
                rm(args=None, recursive=False, show_help=True)
            elif cmd == "mkdir":
                mkdir(remotes=None, show_help=True)
            elif cmd == "touch":
                touch(remotes=None, show_help=True)
            elif cmd == "info":
                info(show_help=True)
            elif cmd == "exec":
                exec_cmd(code="", show_help=True)
            elif cmd == "repl":
                repl(show_help=True)
            elif cmd == "run":
                # Show special help for run in shell (only -d mode)
                shell_console.print(Panel("""\
Run a script from device storage.
In shell mode, 'run' always runs from device (equivalent to 'replx run -d').

[bold cyan]Usage:[/bold cyan]
  run [yellow]SCRIPT_FILE[/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]SCRIPT_FILE[/yellow]  Script file path on device [red][required][/red]

[bold cyan]Examples:[/bold cyan]
  run main.py           [dim]# Run /main.py from device[/dim]
  run lib/test.py       [dim]# Run /lib/test.py from device[/dim]
  run t1.mpy            [dim]# Run .mpy file from device[/dim]

[bold yellow]Note:[/bold yellow]
  In shell mode, -e and -n options are not available.
  Use 'replx run' directly for those options.""", border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
            else:
                shell_console.print(f"No help available for '{cmd}'")
        except typer.Exit:
            pass  # Help displayed, exit was raised

    def run_shell_cmd(cmdline):
        nonlocal current_path

        args = shlex.split(cmdline)
        if not args:
            return
        cmd = args[0]
        
        # Check if command is excluded
        if cmd in EXCLUDED_COMMANDS:
            OutputHelper.print_panel(
                f"[yellow]'{cmd}'[/yellow] is not available in shell mode.",
                title="Command Not Available",
                border_style="yellow"
            )
            return
        
        # Check if command is valid
        if cmd not in SHELL_COMMANDS:
            OutputHelper.print_panel(
                f"[red]'{cmd}'[/red] is not a valid command.\n\nType [bright_blue]help[/bright_blue] or [bright_blue]?[/bright_blue] to see available commands.",
                title="Unknown Command",
                border_style="red"
            )
            return

        try:
            if cmd == "help" or cmd == "?":
                if len(args) > 1:
                    print_shell_help(args[1])
                else:
                    # Show available commands
                    from rich.panel import Panel
                    shell_console = Console(width=CONSOLE_WIDTH)
                    help_text = """\
[bold cyan]Commands:[/bold cyan]
  [yellow]ls[/yellow] [path] [-r]      List files/directories
  [yellow]cat[/yellow] <file>          Display file contents
  [yellow]cp[/yellow] <src...> <dst>   Copy files (use -r for directories)
  [yellow]mv[/yellow] <src...> <dst>   Move/rename files (use -r for directories)
  [yellow]rm[/yellow] <files...>       Remove files (use -r for directories)
  [yellow]mkdir[/yellow] <dirs...>     Create directories
  [yellow]touch[/yellow] <files...>    Create empty files
  [yellow]info[/yellow]                Show device information
  [yellow]exec[/yellow] <code>         Execute Python code
  [yellow]repl[/yellow]                Enter Python REPL
  [yellow]run[/yellow] <script>        Run script from device
  [yellow]cd[/yellow] <dir>            Change directory
  [yellow]pwd[/yellow]                 Print current directory
  [yellow]clear[/yellow]               Clear screen
  [yellow]edit[/yellow] <file>          Edit file in VSCode
  [yellow]exit[/yellow]                Exit shell

[dim]Type 'help <command>' for detailed help on a specific command.[/dim]"""
                    shell_console.print(Panel(help_text, title="Available Commands", border_style="cyan", box=get_panel_box(), width=CONSOLE_WIDTH))
                return
                
            elif cmd == "exit":
                raise SystemExit()
                
            elif cmd == "pwd":
                if "--help" in args or "-h" in args:
                    print_shell_help("pwd")
                    return
                print(current_path)
                return
                
            elif cmd == "clear":
                if "--help" in args or "-h" in args:
                    print_shell_help("clear")
                    return
                OutputHelper._console.clear()
                return
                
            elif cmd == "cd":
                if "--help" in args or "-h" in args:
                    print_shell_help("cd")
                    return
                    
                if len(args) != 2:
                    print("Usage: cd <directory>")
                    return
                
                new_path = posixpath.normpath(posixpath.join(current_path, args[1]))
                try:
                    from replx.agent.client import AgentClient
                    client = AgentClient(port=_get_agent_port())
                    result = client.send_command('is_dir', path=new_path)
                    is_dir = result if isinstance(result, bool) else result.get('is_dir', False)
                    if is_dir:
                        current_path = new_path
                    else:
                        print(f"cd: {args[1]}: Not a directory")
                except Exception:
                    print(f"cd: {args[1]}: No such directory")
                return
                
            elif cmd == "ls":
                if "--help" in args or "-h" in args:
                    print_shell_help("ls")
                    return
                    
                # Parse: ls [path] [-r]
                path_arg = current_path
                recursive = False
                
                for arg in args[1:]:
                    if arg in ("-r", "--recursive"):
                        recursive = True
                    elif not arg.startswith('-'):
                        path_arg = posixpath.normpath(posixpath.join(current_path, arg))
                
                ls(path=path_arg, recursive=recursive, show_help=False)
                return
                
            elif cmd == "cat":
                if "--help" in args or "-h" in args:
                    print_shell_help("cat")
                    return
                    
                # Parse: cat [options] <file>
                number = False
                lines_opt = None
                file_arg = None
                encoding = "utf-8"
                
                i = 1
                while i < len(args):
                    arg = args[i]
                    if arg in ("-n", "--number"):
                        number = True
                    elif arg in ("-L", "--lines"):
                        if i + 1 < len(args):
                            lines_opt = args[i + 1]
                            i += 1
                    elif arg in ("-e", "--encoding"):
                        if i + 1 < len(args):
                            encoding = args[i + 1]
                            i += 1
                    elif not arg.startswith('-'):
                        file_arg = arg
                    i += 1
                
                if not file_arg:
                    print("Usage: cat <file>")
                    return
                    
                remote = posixpath.normpath(posixpath.join(current_path, file_arg))
                cat(remote=remote, encoding=encoding, number=number, lines=lines_opt, show_help=False)
                return
                
            elif cmd == "cp":
                if "--help" in args or "-h" in args:
                    print_shell_help("cp")
                    return
                    
                # Parse: cp [-r] <sources...> <dest>
                recursive = False
                file_args = []
                
                for arg in args[1:]:
                    if arg in ("-r", "--recursive"):
                        recursive = True
                    else:
                        file_args.append(arg)
                
                if len(file_args) < 2:
                    print("Usage: cp [-r] <source...> <dest>")
                    return
                
                # Convert relative paths to absolute
                abs_args = [posixpath.normpath(posixpath.join(current_path, arg)) for arg in file_args]
                cp(args=abs_args, recursive=recursive, show_help=False)
                return
                
            elif cmd == "mv":
                if "--help" in args or "-h" in args:
                    print_shell_help("mv")
                    return
                    
                # Parse: mv [-r] <sources...> <dest>
                recursive = False
                file_args = []
                
                for arg in args[1:]:
                    if arg in ("-r", "--recursive"):
                        recursive = True
                    else:
                        file_args.append(arg)
                
                if len(file_args) < 2:
                    print("Usage: mv [-r] <source...> <dest>")
                    return
                
                abs_args = [posixpath.normpath(posixpath.join(current_path, arg)) for arg in file_args]
                mv(args=abs_args, recursive=recursive, show_help=False)
                return
                
            elif cmd == "rm":
                if "--help" in args or "-h" in args:
                    print_shell_help("rm")
                    return
                    
                # Parse: rm [-r] <files...>
                recursive = False
                file_args = []
                
                for arg in args[1:]:
                    if arg in ("-r", "--recursive"):
                        recursive = True
                    else:
                        file_args.append(arg)
                
                if not file_args:
                    print("Usage: rm [-r] <files...>")
                    return
                
                abs_args = [posixpath.normpath(posixpath.join(current_path, arg)) for arg in file_args]
                rm(args=abs_args, recursive=recursive, show_help=False)
                return
                
            elif cmd == "mkdir":
                if "--help" in args or "-h" in args:
                    print_shell_help("mkdir")
                    return
                    
                if len(args) < 2:
                    print("Usage: mkdir <directories...>")
                    return
                
                abs_args = [posixpath.normpath(posixpath.join(current_path, arg)) for arg in args[1:]]
                mkdir(remotes=abs_args, show_help=False)
                return
                
            elif cmd == "touch":
                if "--help" in args or "-h" in args:
                    print_shell_help("touch")
                    return
                    
                if len(args) < 2:
                    print("Usage: touch <files...>")
                    return
                
                abs_args = [posixpath.normpath(posixpath.join(current_path, arg)) for arg in args[1:]]
                touch(remotes=abs_args, show_help=False)
                return
                
            elif cmd == "info":
                if "--help" in args or "-h" in args:
                    print_shell_help("info")
                    return
                info(show_help=False)
                return
                
            elif cmd == "exec":
                if "--help" in args or "-h" in args:
                    print_shell_help("exec")
                    return
                    
                if len(args) < 2:
                    print("Usage: exec <python_code>")
                    return
                
                # Join remaining args as code
                code = ' '.join(args[1:])
                exec_cmd(code=code, show_help=False)
                return
                
            elif cmd == "repl":
                if "--help" in args or "-h" in args:
                    print_shell_help("repl")
                    return
                repl(show_help=False)
                return
                
            elif cmd == "run":
                if "--help" in args or "-h" in args:
                    print_shell_help("run")
                    return
                    
                # In shell mode, run always uses -d (device mode)
                # -e and -n options are NOT allowed
                if "-e" in args or "--echo" in args:
                    print("Error: -e/--echo option is not available in shell mode.")
                    return
                if "-n" in args or "--non-interactive" in args:
                    print("Error: -n/--non-interactive option is not available in shell mode.")
                    return
                    
                if len(args) != 2:
                    print("Usage: run <script_file>")
                    return
                
                # Build remote path
                script_file = args[1]
                if script_file.startswith('/'):
                    remote_path = script_file
                else:
                    remote_path = posixpath.normpath(posixpath.join(current_path, script_file))
                
                # Call run with device=True (equivalent to replx run -d)
                run(script_file=remote_path, non_interactive=False, echo=False, device=True, show_help=False)
                return
                
            elif cmd == "edit":
                if "--help" in args or "-h" in args:
                    print_shell_help("edit")
                    return
                    
                if len(args) != 2:
                    print("Usage: edit <file>")
                    return
                
                # Build remote path
                file_arg = args[1]
                if file_arg.startswith('/'):
                    remote_path = file_arg
                else:
                    remote_path = posixpath.normpath(posixpath.join(current_path, file_arg))
                
                # Create .temp folder in current working directory
                temp_dir = os.path.join(os.getcwd(), '.temp')
                os.makedirs(temp_dir, exist_ok=True)
                
                # Get filename and create local path
                filename = posixpath.basename(remote_path)
                local_path = os.path.join(temp_dir, filename)
                
                try:
                    from replx.agent.client import AgentClient
                    client = AgentClient(port=_get_agent_port())
                    
                    # Check if file exists on device
                    try:
                        result = client.send_command('is_dir', path=remote_path)
                        is_dir = result if isinstance(result, bool) else result.get('is_dir', False)
                        if is_dir:
                            print(f"Error: '{remote_path}' is a directory, not a file.")
                            return
                    except Exception:
                        pass  # File might not exist, will create new
                    
                    # Download file from device
                    original_hash = None
                    try:
                        result = client.send_command('get_to_local', remote_path=remote_path, local_path=local_path)
                        if isinstance(result, dict) and result.get('error'):
                            # File doesn't exist, create empty file
                            with open(local_path, 'w', encoding='utf-8') as f:
                                pass
                            print(f"Creating new file: {remote_path}")
                        else:
                            print(f"Downloaded: {remote_path}")
                    except Exception:
                        # File doesn't exist, create empty file
                        with open(local_path, 'w', encoding='utf-8') as f:
                            pass
                        print(f"Creating new file: {remote_path}")
                    
                    # Calculate original hash
                    with open(local_path, 'rb') as f:
                        original_hash = hashlib.md5(f.read()).hexdigest()
                    
                    # Open in VSCode and wait
                    print(f"Opening in VSCode... (close the file tab to continue)")
                    try:
                        subprocess.run(['code', '--wait', local_path], shell=True)
                    except FileNotFoundError:
                        print("Error: 'code' command not found. Make sure VSCode is in PATH.")
                        return
                    
                    # Calculate new hash
                    with open(local_path, 'rb') as f:
                        new_hash = hashlib.md5(f.read()).hexdigest()
                    
                    # Check if file was modified
                    if new_hash == original_hash:
                        print("No changes detected.")
                    else:
                        # Ask user if they want to upload
                        print(f"File was modified. Apply the changes? [y/N]: ", end="", flush=True)
                        response = sys.stdin.buffer.readline().decode(errors='replace').strip().lower()
                        
                        if response == 'y':
                            result = client.send_command('put_from_local', local_path=local_path, remote_path=remote_path)
                            if isinstance(result, dict) and result.get('error'):
                                print(f"Upload failed: {result.get('error')}")
                            else:
                                file_size = os.path.getsize(local_path)
                                print(f"Uploaded: {remote_path} ({file_size} bytes)")
                        else:
                            print("Changes discarded.")
                
                finally:
                    # Clean up .temp folder
                    try:
                        if os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                return
                
        except typer.Exit:
            pass  # Command completed normally
        except SystemExit:
            raise  # Re-raise for exit command
        except Exception as e:
            print(f"Error: {e}")
    
    # Display shell header
    header_content = f"Connected to [bright_yellow]{STATE.device}[/bright_yellow] on [bright_green]{STATE.core}[/bright_green]\n\n"
    header_content += "Type [bright_blue]help[/bright_blue] or [bright_blue]?[/bright_blue] to see available commands\n"
    header_content += "Type [bright_blue]exit[/bright_blue] to quit shell"
    
    OutputHelper.print_panel(
        header_content,
        title="Interactive Shell",
        border_style="cyan"
    )

    # Setup signal handler for Ctrl+C
    shell_running = True
    
    def signal_handler(sig, frame):
        nonlocal shell_running
        print("\nType 'exit' to quit shell.")
    
    old_handler = signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while shell_running:
            try:
                print_prompt()
                line = sys.stdin.buffer.readline().decode(errors='replace').rstrip()
                if not line:
                    continue
                try:
                    run_shell_cmd(line)
                except SystemExit:
                    break
                except Exception as e:
                    print(f"Error: {e}")
            except EOFError:
                break
            
    finally:
        signal.signal(signal.SIGINT, old_handler)
        OutputHelper.print_panel(
            "Shell session ended.",
            title="Exit Shell",
            border_style="cyan"
        )


@app.command()
def reset(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Reset the connected device.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Reset the connected device (Ctrl+C to interrupt + Ctrl+D to soft reset).

[bold cyan]Usage:[/bold cyan]
  replx reset

[bold cyan]Examples:[/bold cyan]
  replx reset                        [dim]# Reset device[/dim]

[bold yellow]Note:[/bold yellow]
  If code catches KeyboardInterrupt in infinite loops,
  soft reset may fail. In that case, physically reset the device."""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    status = _ensure_connected()
    
    try:
        with AgentClient(port=_get_agent_port()) as client:
            client.send_command('reset')
        
        # Free agent connection after reset for EFR32MG (XBee3)
        # EFR32MG reset invalidates the connection
        # Other cores may maintain connection after soft reset
        if status.get('core') == 'EFR32MG':
            try:
                client = AgentClient(port=_get_agent_port())
                client.send_command('free')
            except Exception:
                pass  # Ignore errors - agent may already be gone
        
        device = status.get('device', 'unknown')
        OutputHelper.print_panel(
            f"Device [bright_yellow]{device}[/bright_yellow] has been reset.",
            title="Reset Device",
            border_style="blue"
        )
    except Exception as e:
        error_msg = str(e)
        if "soft reset failed" in error_msg.lower():
            OutputHelper.print_panel(
                f"Reset failed: {error_msg}\n\n"
                "[yellow]Tip:[/yellow] If code catches KeyboardInterrupt, soft reset cannot work.\n"
                "Physically press the reset button on your device.",
                title="Reset Error",
                border_style="red"
            )
        else:
            OutputHelper.print_panel(
                f"Reset failed: {error_msg}",
                title="Reset Error",
                border_style="red"
            )
        raise typer.Exit(1)


@app.command(name="update")
def update(
    device: Optional[str] = typer.Argument(None, help="Device name"),
    owner: str = typer.Option("PlanXLab", help="GitHub repository owner"),
    repo: str = typer.Option("replx_libs", help="GitHub repository name"),
    ref: str = typer.Option("main", help="Git reference (branch/tag)"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Update the local library store for the specified device or the connected device.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Update the local library store for the specified device or the connected device.

[bold cyan]Usage:[/bold cyan]
  replx update [[yellow]DEVICE[/yellow]]

[bold cyan]Arguments:[/bold cyan]
  [yellow]device[/yellow]       Optional device name to update

[bold cyan]Options:[/bold cyan]
  --owner         GitHub repository owner (default: PlanXLab)
  --repo          GitHub repository name (default: replx_libs)
  --ref           Git reference (branch/tag, default: main)

[bold cyan]Examples:[/bold cyan]
  replx update                       [dim]# Update for connected device[/dim]
  replx update RP2350                [dim]# Update for specific device[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    # No device communication needed - just download from GitHub
    StoreManager.ensure_home_store()

    core = None
    dev = None
    
    if device:
        # Explicit device specified
        resolved_core = DeviceValidator.find_core_by_device(device)
        if not resolved_core:
            raise typer.Exit(f"Unsupported device: {device}")
        core, dev = resolved_core, device
    else:
        # Try to get device/core from running agent first
        agent_port = _get_agent_port()
        if AgentClient.is_agent_running(port=agent_port):
            try:
                with AgentClient(port=agent_port) as client:
                    status = client.send_command('status', timeout=1.0)
                if status.get('connected'):
                    dev = status.get('device', '').strip()
                    core = status.get('core', '').strip()
            except Exception:
                pass
        
        # Fallback: try to get device/core from .replx file
        if not core:
            env_path = _find_env_file()
            if env_path:
                config = _read_env_config(env_path)
                dev = config.get('device', '').strip() or dev
                core = config.get('core', '').strip() or core
        
        if not core:
            OutputHelper.print_panel(
                "Device information not available.\n"
                "Use [bright_blue]replx setup --port PORT[/bright_blue] first or specify device with [bright_blue]replx update <device>[/bright_blue].",
                title="Device Required",
                border_style="red"
            )
            raise typer.Exit(1)

    try:
        remote = StoreManager.load_remote_meta(owner, repo, ref)
    except Exception as e:
        raise typer.BadParameter(f"Failed to load remote meta: {e}")

    # Check if core and device exist in remote registry
    cores, devices = RegistryHelper.root_sections(remote)
    
    core_exists_remote = core in cores if core else False
    # If core == device, treat device as not existing (only process core)
    device_exists_remote = (dev in devices if dev else False) and (dev != core)
    
    # Check if core and device exist locally
    core_src_path = os.path.join(StoreManager.pkg_root(), "core", core, "src") if core else ""
    device_src_path = os.path.join(StoreManager.pkg_root(), "device", dev, "src") if dev and dev != core else ""
    
    core_exists_local = os.path.isdir(core_src_path) if core_src_path else False
    device_exists_local = os.path.isdir(device_src_path) if device_src_path else False
    
    # Step 1: Handle core
    if not core_exists_local:
        # Core not in local - need to download
        if not core_exists_remote:
            OutputHelper.print_panel(
                f"Core [yellow]{core}[/yellow] not found in remote registry.",
                title="Notice",
                border_style="yellow"
            )
            raise typer.Exit(0)
        # Core exists remotely, will download below
    
    # Step 2: Handle device (only if core is already local and device is different from core)
    if core_exists_local:
        # Core already exists, check device (only if different from core)
        if dev == core or device_exists_local or not device_exists_remote:
            # Device same as core, or device already local, or device not in remote
            # All cases: nothing more to download
            OutputHelper.print_panel(
                f"Core [bright_green]{core}[/bright_green] is already up to date.",
                title="Update Complete",
                border_style="green"
            )
            raise typer.Exit(0)

    try:
        local = StoreManager.load_local_meta()
        if not isinstance(local, dict):
            local = {}
    except Exception:
        local = {}

    items_local = local.setdefault("items", {})
    items_local.setdefault("core", {})
    items_local.setdefault("device", {})
    if "targets" in remote:
        local["targets"] = remote.get("targets") or {}

    def _local_touch_file(scope: str, target: str, part: str, relpath: str, ver: float) -> None:
        scope_node = items_local.setdefault(scope, {})
        tgt_node = scope_node.setdefault(target, {})
        part_node = tgt_node.setdefault(part, {})
        files = part_node.setdefault("files", {})
        segs = relpath.split("/")
        cur = files
        for i, seg in enumerate(segs):
            last = (i == len(segs) - 1)
            ent = cur.get(seg)
            if last:
                if not isinstance(ent, dict) or "files" in (ent or {}):
                    ent = {}
                ent["ver"] = float(ver)
                cur[seg] = ent
            else:
                if not isinstance(ent, dict) or "files" not in ent:
                    ent = {"files": {}}
                    cur[seg] = ent
                cur = ent["files"]

    exts = (".py", ".pyi", ".json")
    bar_len = 40

    def _plan(scope: str, target: str, part: str) -> list[tuple[str, float]]:
        node = RegistryHelper.get_node(remote, scope, target)
        part_node = node.get(part) or {}
        if not part_node:
            return []
        todo: list[tuple[str, float]] = []
        for relpath, _leaf_meta in RegistryHelper.walk_files(part_node, ""):
            if not relpath.endswith(exts):
                continue
            rver = RegistryHelper.effective_version(remote, scope, target, part, relpath)
            try:
                lver = RegistryHelper.effective_version(local, scope, target, part, relpath)
            except Exception:
                lver = 0.0
            if float(lver or 0.0) < float(rver or 0.0):
                todo.append((relpath, rver))
        return todo

    # Build plan based on what needs to be downloaded
    plan = []
    download_target = ""
    
    if not core_exists_local and core_exists_remote:
        # Download core only
        plan += (
            [( "core",  core,  "src",       *x) for x in _plan("core",  core,  "src")] +
            [( "core",  core,  "typehints", *x) for x in _plan("core",  core,  "typehints")]
        )
        download_target = f"core/{core}"
    elif core_exists_local and not device_exists_local and device_exists_remote:
        # Core exists, download device only
        plan += (
            [( "device",dev,   "src",       *x) for x in _plan("device",dev,   "src")] +
            [( "device",dev,   "typehints", *x) for x in _plan("device",dev,   "typehints")]
        )
        download_target = f"device/{dev}"
    
    total = len(plan)

    if total > 0:
        done = 0
        done_lock = threading.Lock()
        current_file = [""]
        errors = []
        
        def download_file(task):
            """Download a single file (for parallel execution)"""
            scope, target, part, relpath, rver = task
            repo_path = f"{scope}/{target}/{part}/{relpath}"
            out_path = os.path.join(StoreManager.pkg_root(), repo_path.replace("/", os.sep))
            
            try:
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                InstallHelper.download_raw_file(owner, repo, ref, repo_path, out_path)
                _local_touch_file(scope, target, part, relpath, rver)
                return (True, relpath, None)
            except urllib.error.HTTPError as e:
                # HTTP errors (404, 403, etc.) - file doesn't exist on GitHub
                # Generate the URL for debugging
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{repo_path}"
                return (False, relpath, f"404 Not Found - URL: {url}")
            except OSError as e:
                # Local filesystem errors (permissions, disk full, etc.)
                return (False, relpath, f"Local: {e}")
            except Exception as e:
                return (False, relpath, str(e))
        
        # Parallel download with ThreadPoolExecutor
        # Use 4 threads by default for optimal balance between speed and API limits
        # Can be configured via REPLX_DOWNLOAD_THREADS environment variable
        default_workers = 4
        max_workers = min(
            int(os.environ.get("REPLX_DOWNLOAD_THREADS", str(default_workers))),
            total,
            8  # Cap at 8 to avoid rate limiting
        )
        
        with Live(OutputHelper.create_progress_panel(done, total, title=f"Updating {download_target}", message=f"Downloading {total} file(s)..."), console=OutputHelper._console, refresh_per_second=10) as live:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all download tasks
                future_to_task = {executor.submit(download_file, task): task for task in plan}
                
                # Process completed downloads
                for future in as_completed(future_to_task):
                    success, relpath, error = future.result()
                    
                    with done_lock:
                        done += 1
                        current_file[0] = relpath
                        
                        if not success:
                            errors.append(f"{relpath}: {error}")
                        
                        live.update(OutputHelper.create_progress_panel(
                            done, total, 
                            title=f"Updating {download_target}", 
                            message=f"Downloading... {relpath} ({done}/{total})"
                        ))
        
        # Check for errors
        if errors:
            OutputHelper._console.print("\n[red]Download errors:[/red]")
            for err in errors[:5]:  # Show first 5 errors
                OutputHelper._console.print(f"  [yellow]•[/yellow] {err}")
            if len(errors) > 5:
                OutputHelper._console.print(f"  [dim]... and {len(errors) - 5} more errors[/dim]")
            
            # Provide helpful guidance
            OutputHelper._console.print("\n[yellow]Possible causes:[/yellow]")
            OutputHelper._console.print("  1. Files don't exist in the repository")
            OutputHelper._console.print("  2. Repository branch/tag mismatch")
            OutputHelper._console.print(f"  3. Check repository: https://github.com/{owner}/{repo}/tree/{ref}")
            
            raise typer.BadParameter(f"Failed to download {len(errors)} file(s)")

    StoreManager.save_local_meta(local)
    
    # Show completion panel
    if total == 0:
        message = f"[bright_green]{download_target}[/bright_green] is already up to date."
    else:
        message = f"[bright_green]{download_target}[/bright_green]: [green]{total}[/green] file(s) downloaded."
    
    OutputHelper.print_panel(
        message,
        title="Update Complete",
        border_style="green"
    )

INSTALL_HELP = """\
SPEC can be:
  (empty)             Install all core and device libs/files.
  core/               Install core libs into /lib/...
  device/             Install device libs into /lib/<device>/...
  ./foo.py            -> /lib/foo.mpy
  ./main.py|boot.py   -> /main.mpy or /boot.mpy
  ./app/              -> /app (folder)
  https://.../x.py    -> /lib/x.mpy
"""

def _install_spec_internal(spec: str):
    """
    Internal helper to install a spec without CLI recursion.
    Used to maintain REPL session when installing multiple specs (core + device).
    
    Flattens ext/<domain>/<target>/*.py to lib/<device>/ext/*.mpy for deployment.
    
    :param spec: Specification string (e.g., "core/", "device/")
    """
    if spec.startswith("core/") or spec.startswith("device/"):
        scope, rest = InstallHelper.resolve_spec(spec)
        base, local_list = InstallHelper.list_local_py_targets(scope, rest)
        if not local_list:
            raise typer.BadParameter("No local files to install. Run 'replx update' first.")

        total = len(local_list)
        
        # Pre-compile and prepare batch specs
        batch_specs = []
        unique_dirs = set()
        for abs_py, rel in local_list:
            rel_dir = os.path.dirname(rel)
            
            # Flatten ext/<domain>/<target>/*.py to ext/*.mpy
            if rel.startswith("ext/") and "/" in rel[4:]:
                # Extract: ext/<domain>/<target>/file.py -> ext/file.mpy
                parts = rel.split("/")
                if len(parts) >= 3:  # ext/<domain>/<target>/...
                    # Keep only ext/ + filename
                    flattened_rel = "ext/" + parts[-1]
                    rel_dir = "ext"
                    remote_dir = InstallHelper.remote_dir_for(scope, rel_dir)
                    
                    CompilerHelper.compile_to_staging(abs_py, base)
                    out_mpy = CompilerHelper.staging_out_for(abs_py, base, CompilerHelper.mpy_arch_tag())
                    remote_path = (STATE.device_root_fs + remote_dir + os.path.splitext(parts[-1])[0] + ".mpy").replace("//", "/")
                    
                    batch_specs.append((out_mpy, remote_path))
                    unique_dirs.add(remote_dir)
                    continue
            
            # Normal processing for non-ext files
            remote_dir = InstallHelper.remote_dir_for(scope, rel_dir)
            
            CompilerHelper.compile_to_staging(abs_py, base)
            out_mpy = CompilerHelper.staging_out_for(abs_py, base, CompilerHelper.mpy_arch_tag())
            remote_path = (STATE.device_root_fs + remote_dir + os.path.splitext(os.path.basename(rel))[0] + ".mpy").replace("//", "/")
            
            batch_specs.append((out_mpy, remote_path))
            
            # Collect all unique directory paths
            if remote_dir:
                unique_dirs.add(remote_dir)
        
        # Create all directories in a single REPL session with batched mkdir commands
        if unique_dirs:
            from replx.agent.client import AgentClient
            client = AgentClient(port=_get_agent_port())
            
            # Collect all mkdir paths in proper order (parent before child)
            all_paths = set()
            for remote_dir in sorted(unique_dirs):
                parts = [p for p in remote_dir.replace("\\", "/").strip("/").split("/") if p]
                path = STATE.device_root_fs.rstrip("/")
                for p in parts:
                    path = path + "/" + p
                    all_paths.add(path)
            
            # Create directories using agent mkdir command (handles nested dirs)
            for path in sorted(all_paths):
                try:
                    client.send_command('mkdir', path=path)
                except Exception:
                    pass  # Directory may already exist
        
        # Use agent for batch upload with streaming byte-level progress
        from replx.agent.client import AgentClient
        import threading
        client = AgentClient(port=_get_agent_port())
        
        # Track progress state for each file
        progress_state = {
            "file_idx": 0,
            "total_files": total,
            "current_file": "",
            "bytes_sent": 0,
            "bytes_total": 0,
            "completed": False,
            "error": None
        }
        progress_lock = threading.Lock()
        
        def progress_callback(data):
            """Handle streaming progress from agent."""
            with progress_lock:
                if isinstance(data, dict):
                    progress_state["bytes_sent"] = data.get("current", 0)
                    progress_state["bytes_total"] = data.get("total", 0)
        
        def upload_file(local_path: str, remote_path: str) -> dict:
            """Upload a single file with streaming progress."""
            try:
                return client.send_command_streaming(
                    'put_from_local_streaming',
                    progress_callback=progress_callback,
                    local_path=local_path,
                    remote_path=remote_path
                )
            except Exception as e:
                return {"error": str(e)}
        
        with Live(OutputHelper.create_progress_panel(0, total, title=f"Installing {spec} to {STATE.device}", message=f"Processing {total} file(s)..."), console=OutputHelper._console, refresh_per_second=10) as live:
            for idx, (local_path, remote_path) in enumerate(batch_specs):
                filename = os.path.basename(local_path)
                file_size = os.path.getsize(local_path) if os.path.exists(local_path) else 0
                
                with progress_lock:
                    progress_state["file_idx"] = idx
                    progress_state["current_file"] = filename
                    progress_state["bytes_sent"] = 0
                    progress_state["bytes_total"] = file_size
                
                # Start upload in background thread
                upload_result = [None]
                def do_upload():
                    upload_result[0] = upload_file(local_path, remote_path)
                
                upload_thread = threading.Thread(target=do_upload, daemon=True)
                upload_thread.start()
                
                # Update progress bar while uploading
                while upload_thread.is_alive():
                    with progress_lock:
                        bytes_sent = progress_state["bytes_sent"]
                        bytes_total = progress_state["bytes_total"]
                    
                    if bytes_total > 0:
                        pct = int(bytes_sent * 100 / bytes_total)
                        msg = f"[{idx+1}/{total}] {filename} ({bytes_sent}/{bytes_total} bytes)"
                    else:
                        msg = f"[{idx+1}/{total}] {filename}..."
                    
                    live.update(OutputHelper.create_progress_panel(idx, total, title=f"Installing {spec} to {STATE.device}", message=msg))
                    time.sleep(0.1)
                
                upload_thread.join()
                
                # Check result
                resp = upload_result[0]
                if resp and resp.get('error'):
                    # Log error but continue
                    pass
            
            live.update(OutputHelper.create_progress_panel(total, total, title=f"Installing {spec} to {STATE.device}", message="Complete"))
        
        OutputHelper.print_panel(
            f"[green]{total}[/green] file(s) installed successfully.",
            title="Installation Complete",
            border_style="green"
        )
    else:
        raise typer.BadParameter(f"Invalid spec format: {spec}")

@app.command(
    name="install",
    help="Install libraries/files onto the device.\n\n" + INSTALL_HELP
)
def install(
    spec: Optional[str] = typer.Argument(None, metavar="SPEC", help="Target specification"),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Install libraries/files onto the device.

[bold cyan]Usage:[/bold cyan]
  replx install [yellow][SPEC][/yellow]

[bold cyan]Arguments:[/bold cyan]
  [yellow]spec[/yellow]        Target specification

  spec can be:
  [dim](empty)[/dim]                 Install all core and device libs/files
  [green]core/[/green]                   Install core libs into /lib/...
  [green]device/[/green]                 Install device libs into /lib/<device>/...
  [green]./<name>.py[/green]             -> /lib/<name>.mpy
  [green]./main.py | boot.py[/green]     -> /main.mpy or /boot.mpy
  [green]./<folder>/[/green]             -> /<folder>
  [green]https://.../<name>.py[/green]   -> /lib/<name>.mpy

[bold cyan]Examples:[/bold cyan]
  replx install                      [dim]# Install all core and device libs[/dim]
  replx install core/                [dim]# Install core libs only[/dim]
  replx install ./main.py            [dim]# Install single file[/dim]
  replx install ./app                [dim]# Install directory[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    _ensure_connected()

    StoreManager.ensure_home_store()

    def _install_local_folder(abs_dir: str):
        # Count total files first
        py_files = []
        for dp, _, fns in os.walk(abs_dir):
            for fn in fns:
                if fn.endswith(".py"):
                    py_files.append(os.path.join(dp, fn))
        
        total = len(py_files)
        if total == 0:
            OutputHelper.print_panel(
                f"No Python files found in [yellow]{abs_dir}[/yellow]",
                title="Installation",
                border_style="yellow"
            )
            return 0
        
        installed = 0
        base = abs_dir
        
        # Pre-compile all files to staging
        compiled_files = []
        for ap in py_files:
            CompilerHelper.compile_to_staging(ap, base)
            rel = os.path.relpath(ap, base).replace("\\", "/")
            remote = (STATE.device_root_fs + rel).replace("\\", "/")
            remote = remote[:-3] + ".mpy"
            out_mpy = CompilerHelper.staging_out_for(ap, base, CompilerHelper.mpy_arch_tag())
            compiled_files.append((out_mpy, remote, os.path.dirname(rel)))
        
        # Create all necessary remote directories
        for _, _, rel_dir in compiled_files:
            try:
                InstallHelper.ensure_remote_dir(rel_dir)
            except Exception:
                pass
        
        # Use agent for batch upload with progress
        from replx.agent.client import AgentClient
        client = AgentClient(port=_get_agent_port())
        
        with Live(OutputHelper.create_progress_panel(0, total, title=f"Installing {os.path.basename(abs_dir)} to {STATE.device}", message=f"Processing {total} file(s)..."), console=OutputHelper._console, refresh_per_second=10) as live:
            for idx, (local_mpy, remote, _) in enumerate(compiled_files):
                filename = os.path.basename(local_mpy)
                live.update(OutputHelper.create_progress_panel(idx, total, title=f"Installing {os.path.basename(abs_dir)} to {STATE.device}", message=f"Uploading {filename}..."))
                
                resp = client.send_command('put_from_local', local_path=local_mpy, remote_path=remote)
                if resp.get('status') != 'ok':
                    # Log error but continue
                    pass
            
            installed = total
            live.update(OutputHelper.create_progress_panel(total, total, title=f"Installing {os.path.basename(abs_dir)} to {STATE.device}", message="Complete"))
        
        OutputHelper.print_panel(
            f"[green]{installed}[/green] file(s) installed successfully.",
            title="Installation Complete",
            border_style="green"
        )
        return installed

    def _install_single_file(abs_py: str):
        base = os.path.dirname(abs_py)
        name = os.path.basename(abs_py)
        
        with Live(OutputHelper.create_progress_panel(0, 1, title=f"Installing {name} to {STATE.device}", message="Processing..."), console=OutputHelper._console, refresh_per_second=10) as live:
            CompilerHelper.compile_to_staging(abs_py, base)
            out_mpy = CompilerHelper.staging_out_for(abs_py, base, CompilerHelper.mpy_arch_tag())
            if name in ("main.py", "boot.py"):
                remote = (STATE.device_root_fs + name[:-3] + ".mpy").replace("//", "/")
            else:
                remote = (STATE.device_root_fs + "lib/" + name[:-3] + ".mpy").replace("//", "/")
                InstallHelper.ensure_remote_dir("lib")
            
            # Upload using agent
            from replx.agent.client import AgentClient
            client = AgentClient(port=_get_agent_port())
            resp = client.send_command('put_from_local', local_path=out_mpy, remote_path=remote)
            if not resp.get('success'):
                OutputHelper.print_panel(
                    f"Upload failed: [red]{resp.get('error', 'Unknown error')}[/red]",
                    title="Installation Failed",
                    border_style="red"
                )
                return 0
            live.update(OutputHelper.create_progress_panel(1, 1, title=f"Installing {name} to {STATE.device}"))
        
        OutputHelper.print_panel(
            f"[green]1[/green] file installed successfully.",
            title="Installation Complete",
            border_style="green"
        )
        return 1

    if spec and (spec.startswith("core/") or spec.startswith("device/")):
        _install_spec_internal(spec)
        return

    if spec and InstallHelper.is_url(spec):
        u = urlparse(spec)
        fname = os.path.basename(u.path)
        if not fname.endswith(".py"):
            raise typer.BadParameter("Only single .py file is supported for URL installs.")
        dl_dir = StoreManager.HOME_STAGING / "downloads"
        dl_dir.mkdir(parents=True, exist_ok=True)
        dst = str(dl_dir / fname)
        try:
            with urllib.request.urlopen(spec) as r, open(dst, "wb") as f:
                f.write(r.read())
        except Exception as e:
            raise typer.BadParameter(f"Download failed: {e}")
        try:
            _install_single_file(dst)
        finally:
            try:
                os.remove(dst)
            except Exception:
                pass
        return

    if not spec:
        # Check if meta file exists (required for any installation)
        meta_path = StoreManager.local_meta_path()
        if not os.path.isfile(meta_path):
            raise typer.BadParameter(
                "Local store is not ready. Please run 'replx update' first. (meta missing)"
            )
        
        # Check core - required
        core_src = os.path.join(StoreManager.pkg_root(), "core", STATE.core, "src")
        if not os.path.isdir(core_src):
            raise typer.BadParameter(
                f"Core library for {STATE.core} not found. Please run 'replx update' first."
            )
        
        # Prepare install specs
        specs_to_install = ["core/"]
        
        # Check device - optional
        dev_src = os.path.join(StoreManager.pkg_root(), "device", STATE.device, "src")
        if os.path.isdir(dev_src):
            specs_to_install.append("device/")
        
        # Install all specs in sequence, maintaining REPL session
        for spec_item in specs_to_install:
            # Use _install_spec_internal to avoid re-entering CLI callback
            _install_spec_internal(spec_item)

        return

    target = spec
    ap = os.path.abspath(target)
    if os.path.isdir(ap):
        _install_local_folder(ap)
        return
    if os.path.isfile(ap):
        if not ap.endswith(".py"):
            raise typer.BadParameter("Only .py is supported for single-file install.")
        _install_single_file(ap)
        return

    raise typer.BadParameter("Target not found. For specs use core/... or device/..., otherwise pass a local path or URL.")

@app.command()
def search(
    lib_name: Optional[str] = typer.Argument(None, help="Library name to search"),
    owner: str = typer.Option("PlanXLab", help="GitHub owner"),
    repo: str = typer.Option("replx_libs", help="GitHub repository"),
    ref: str = typer.Option("main", help="Branch/Tag/SHA"),
    show_all: bool = typer.Option(False, "--all", hidden=True),
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Search for libraries/files in the remote registry.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Search for libraries/files in the remote registry.

[bold cyan]Usage:[/bold cyan]
  replx search [[yellow]LIB_NAME[/yellow]]

[bold cyan]Arguments:[/bold cyan]
  [yellow]lib_name[/yellow]     Optional library name to search for

[bold cyan]Options:[/bold cyan]
  --owner         GitHub owner (default: PlanXLab)
  --repo          GitHub repository (default: replx_libs)
  --ref           Branch/Tag/SHA (default: main)

[bold cyan]Examples:[/bold cyan]
  replx search                       [dim]# List all libraries[/dim]
  replx search micropython           [dim]# Search for micropython libs[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()
    
    # No device communication needed - just search GitHub registry
    try:
        remote = StoreManager.load_remote_meta(owner, repo, ref)
    except Exception as e:
        raise typer.BadParameter(f"Failed to load remote registry: {e}")

    try:
        local = StoreManager.load_local_meta()
    except Exception:
        local = {}

    cores, devices = RegistryHelper.root_sections(remote)
    targets = remote.get("targets") or {}

    def device_core_of(dev_name: str) -> str | None:
        dnode = devices.get(dev_name) or {}
        return dnode.get("core") or targets.get(dev_name)

    def local_ver(scope: str, target: str, part: str, relpath: str) -> tuple[float, bool]:
        if not local or not isinstance(local, dict):
            return (0.0, True)
        try:
            v = RegistryHelper.effective_version(local, scope, target, part, relpath)
            node = RegistryHelper.get_node(local, scope, target)
            if not node:
                return (v, True)
            return (v, False)
        except Exception:
            return (0.0, True)

    def add_core_rows(core_name: str, rows: list):
        node = RegistryHelper.get_node(remote, "core", core_name)
        part_node = node.get("src") or {}
        for relpath, _leaf_meta in RegistryHelper.walk_files(part_node, ""):
            if not relpath.endswith(".py"):
                continue
            rver = RegistryHelper.effective_version(remote, "core", core_name, "src", relpath)
            lver, missing = local_ver("core", core_name, "src", relpath)
            rows.append(("core", core_name, SearchHelper.fmt_ver_with_star(rver, lver, missing), f"src/{relpath}"))

    def add_device_rows(dev_name: str, rows: list):
        node = RegistryHelper.get_node(remote, "device", dev_name)
        part_node = node.get("src") or {}
        for relpath, _leaf_meta in RegistryHelper.walk_files(part_node, ""):
            if not relpath.endswith(".py"):
                continue
            rver = RegistryHelper.effective_version(remote, "device", dev_name, "src", relpath)
            lver, missing = local_ver("device", dev_name, "src", relpath)
            rows.append(("device", dev_name, SearchHelper.fmt_ver_with_star(rver, lver, missing), f"src/{relpath}"))

    def resolve_current_dev_core() -> tuple[Optional[str], Optional[str]]:
        # Try to get device/core from running agent first
        agent_port = _get_agent_port()
        if AgentClient.is_agent_running(port=agent_port):
            try:
                with AgentClient(port=agent_port) as client:
                    status = client.send_command('status', timeout=1.0)
                if status.get('connected'):
                    cur_dev = status.get('device', '').strip()
                    cur_core = status.get('core', '').strip()
                    if cur_dev or cur_core:
                        dk = SearchHelper.key_ci(devices, cur_dev) if cur_dev else None
                        ck = SearchHelper.key_ci(cores, cur_core) if cur_core else None
                        if ck:
                            return dk, ck
            except Exception:
                pass
        
        # Fallback: try to get device/core from .replx file
        env_path = _find_env_file()
        if env_path:
            config = _read_env_config(env_path)
            cur_dev = config.get('device', '').strip()
            cur_core = config.get('core', '').strip()
            if cur_dev or cur_core:
                dk = SearchHelper.key_ci(devices, cur_dev) if cur_dev else None
                ck = SearchHelper.key_ci(cores, cur_core) if cur_core else None
                if ck:
                    return dk, ck

        return None, None

    rows: list[tuple[str, str, str, str]] = []
    cur_dev_key, cur_core_key = resolve_current_dev_core()

    if show_all:
        for c in sorted(cores.keys(), key=str.lower):
            add_core_rows(c, rows)
        for d in sorted(devices.keys(), key=str.lower):
            add_device_rows(d, rows)
    elif lib_name:
        dkey = SearchHelper.key_ci(devices, lib_name)
        ckey = SearchHelper.key_ci(cores, lib_name)

        if dkey:
            core = device_core_of(dkey)
            core_key = SearchHelper.key_ci(cores, core) if core else None
            if core_key:
                add_core_rows(core_key, rows)
            add_device_rows(dkey, rows)
        elif ckey:
            add_core_rows(ckey, rows)
        else:
            scope_candidates: list[tuple[str, str]] = []
            if cur_dev_key:
                scope_candidates.append(("device", cur_dev_key))
                if cur_core_key:
                    scope_candidates.append(("core", cur_core_key))
            else:
                for c in cores.keys():
                    scope_candidates.append(("core", c))
                for d in devices.keys():
                    scope_candidates.append(("device", d))

            q = lib_name.lower()
            for scope, target in scope_candidates:
                node = RegistryHelper.get_node(remote, scope, target)
                part_node = node.get("src") or {}
                for relpath, _leaf_meta in RegistryHelper.walk_files(part_node, ""):
                    if not relpath.endswith(".py"):
                        continue
                    shown = f"src/{relpath}"
                    if (q in shown.lower()) or (q in target.lower()):
                        rver = RegistryHelper.effective_version(remote, scope, target, "src", relpath)
                        lver, missing = local_ver(scope, target, "src", relpath)
                        rows.append((scope, target, SearchHelper.fmt_ver_with_star(rver, lver, missing), shown))
    else:
        # No lib_name - show libraries for current device/core
        if cur_core_key:
            # Have core - show core libraries
            add_core_rows(cur_core_key, rows)
            # Show device libraries only if device exists in registry and is different from core
            if cur_dev_key and cur_dev_key != cur_core_key:
                add_device_rows(cur_dev_key, rows)
        else:
            # No current device detected - show all
            for c in sorted(cores.keys(), key=str.lower):
                add_core_rows(c, rows)
            for d in sorted(devices.keys(), key=str.lower):
                add_device_rows(d, rows)

    if not rows:
        OutputHelper.print_panel(
            "No results found.",
            title=f"Search Results [{owner}/{repo}@{ref}]",
            border_style="yellow"
        )
        return

    def row_key(r):
        scope_order = 0 if r[0] == "core" else 1
        return (scope_order, r[1].lower(), r[3].lower())

    rows.sort(key=row_key)

    w1 = max(5, max(len(r[0]) for r in rows))  # SCOPE
    w2 = max(6, max(len(r[1]) for r in rows))  # TARGET
    w3 = max(5, max(len(r[2]) for r in rows))  # VER

    lines = []
    lines.append(f"{'SCOPE'.ljust(w1)}   {'TARGET'.ljust(w2)}   {'VER'.ljust(w3)}  FILE")
    lines.append("─" * (80 - 4))
    for scope, target, ver_str, shown_path in rows:
        lines.append(f"{scope.ljust(w1)}   {target.ljust(w2)}   {ver_str.ljust(w3)}  {shown_path[4:]}")
    
    OutputHelper.print_panel(
        "\n".join(lines),
        title=f"Search Results [{owner}/{repo}@{ref}]",
        border_style="magenta"
    )

@app.command()
def scan(
    show_help: bool = typer.Option(False, "--help", "-h", is_eager=True, hidden=True)
):
    """
    Scan and list connected MicroPython boards.
    """
    if show_help:
        from rich.panel import Panel
        console = Console(width=CONSOLE_WIDTH)
        help_text = """\
Scan and list connected MicroPython boards.

[bold cyan]Usage:[/bold cyan]
  replx scan

[bold cyan]Examples:[/bold cyan]
  replx scan                         [dim]# List connected boards[/dim]"""
        console.print(Panel(help_text, border_style="dim", box=get_panel_box(), width=CONSOLE_WIDTH))
        console.print()
        raise typer.Exit()

    from ..agent.client import AgentClient

    color_map = {
        0: "yellow",
        1: "green",
        2: "blue"
    }
    serial_results = []  # List of (port, version, core, device, manufacturer)
    webrepl_results = []  # List of IP addresses
    connected_port = None  # Track currently connected port/IP for highlighting
    connected_type = None  # 'serial' or 'webrepl'
    env_port = None  # Port from .vscode/.replx (for arrow indicator when not connected)
    env_target = None  # WebREPL target from .vscode/.replx

    # ========================================
    # SERIAL SCAN
    # ========================================
    # Get agent UDP port from .replx for multi-device support
    env_path = _find_env_file()
    agent_udp_port = None
    if env_path:
        env_config = _read_env_config(env_path)
        agent_udp_port = env_config.get('agent_port')
    
    # Step 1: Check if agent is running and get its connected port info
    agent_port = None
    agent_connected = False
    if AgentClient.is_agent_running(port=agent_udp_port):
        try:
            with AgentClient(port=agent_udp_port) as client:
                status = client.send_command('status')
                if status.get('connected'):
                    agent_connected = True
                    conn_type = status.get('connection_type', '')
                    if conn_type == 'webrepl':
                        # WebREPL connection - remember IP for highlighting
                        connected_port = status.get('port')  # IP address
                        connected_type = 'webrepl'
                    else:
                        # Serial connection - get _machine string via agent exec
                        agent_port = status.get('port')
                        connected_port = agent_port
                        connected_type = 'serial'
                        
                        # Execute sys.implementation._machine to get full device info
                        try:
                            result = client.send_command('exec', code='import sys; print(sys.implementation._machine)')
                            machine_str = result.get('output', '').strip()
                            if machine_str:
                                # Parse using same logic as banner parsing
                                from ..cli.helpers import parse_device_banner
                                # Create fake banner for parsing: "v<version>; <machine_str>"
                                fake_banner = f"v{status.get('version', '?')}; {machine_str}"
                                parsed = parse_device_banner(fake_banner)
                                if parsed:
                                    version, core, device, manufacturer = parsed
                                    serial_results.append((agent_port, version, core, device, manufacturer))
                                else:
                                    # Parsing failed - use status info with Unknown manufacturer
                                    serial_results.append((
                                        agent_port,
                                        status.get('version') or '?',
                                        status.get('core') or '?',
                                        status.get('device') or '?',
                                        'Unknown'
                                    ))
                            else:
                                # No machine string - use status info
                                serial_results.append((
                                    agent_port,
                                    status.get('version') or '?',
                                    status.get('core') or '?',
                                    status.get('device') or '?',
                                    'Unknown'
                                ))
                        except Exception:
                            # Exec failed - use status info
                            serial_results.append((
                                agent_port,
                                status.get('version') or '?',
                                status.get('core') or '?',
                                status.get('device') or '?',
                                'Unknown'
                            ))
        except Exception:
            pass

    # Step 1.5: If not connected, check .vscode/.replx for configured port
    if not agent_connected:
        if env_path:
            env_config = _read_env_config(env_path)
            env_port = env_config.get('serial_port')
            env_target = env_config.get('target')  # WebREPL target (ws://ip:port)

    # Step 2: Scan remaining serial ports in parallel using banner detection
    # Exclude agent-connected port from scanning
    scanned = DeviceScanner.scan_serial_ports(max_workers=5, exclude_port=agent_port)

    for port_device, board_info in scanned:
        version, core, device, manufacturer = board_info
        serial_results.append((
            port_device,
            version,
            core,
            device,
            manufacturer  # info source is manufacturer
        ))

    # Sort serial results by port number (COM3 < COM10 < COM19)
    def port_sort_key(item):
        port = item[0].upper()
        # Extract numeric part from port name (e.g., COM19 -> 19)
        import re
        match = re.search(r'(\d+)$', port)
        if match:
            return (port[:match.start()], int(match.group(1)))
        return (port, 0)
    
    serial_results.sort(key=port_sort_key)

    # ========================================
    # WEBREPL SCAN
    # ========================================
    # Scan for devices responding on port 8266
    # Note: Cannot get device info without password authentication
    webrepl_scan = NetworkScanner.scan_webrepl_network(max_workers=50)
    for ip, _ in webrepl_scan:
        webrepl_results.append(ip)

    # Sort webrepl results by IP
    webrepl_results.sort(key=lambda x: tuple(map(int, x.split('.'))))

    # ========================================
    # DISPLAY RESULTS
    # ========================================
    # Calculate max widths for alignment
    max_device_len = max((len(r[3]) for r in serial_results), default=8)
    
    # Format Serial section
    serial_lines = []
    for idx, (port, version, core, device, manufacturer) in enumerate(serial_results):
        color = color_map[idx % len(color_map)]
        port_upper = port.upper()  # Always display port in uppercase
        # Highlight connected port with bold nerd font marker (󰁔), background color, white text
        # Marker + space = 2 chars, so use same prefix width for alignment
        if connected_type == 'serial' and connected_port and port.upper() == connected_port.upper():
            port_fmt = f"[bold white on {color}]󰁔[/bold white on {color}][white on {color}] {port_upper:>6}[/white on {color}]"
        elif env_port and port.upper() == env_port.upper():
            # Show arrow indicator for .replx configured port when not connected
            port_fmt = f"[dim]→[/dim] [{color}]{port_upper:>6}[/{color}]"
        else:
            port_fmt = f"  [{color}]{port_upper:>6}[/{color}]"
        # Tab-aligned: port  version  core  device  manufacturer (no parentheses)
        line = f"{port_fmt}  {version:<8} {core:<8} [{color}]{device:<{max_device_len}}[/{color}]  [dim]{manufacturer}[/dim]"
        serial_lines.append(line)

    # Format WebREPL section
    # Extract IP from env_target (ws://ip:port format)
    env_webrepl_ip = None
    if env_target and env_target.startswith('ws://'):
        try:
            # Parse ws://ip:port to extract IP
            target_part = env_target[5:]  # Remove 'ws://'
            env_webrepl_ip = target_part.split(':')[0]
        except Exception:
            pass

    webrepl_lines = []
    for idx, ip in enumerate(webrepl_results):
        color = color_map[idx % len(color_map)]
        # Highlight connected IP with bold nerd font marker (󰁔), background color, white text
        if connected_type == 'webrepl' and connected_port and ip == connected_port:
            webrepl_lines.append(f"[bold white on {color}]󰁔[/bold white on {color}][white on {color}] {ip}[/white on {color}]")
        elif env_webrepl_ip and ip == env_webrepl_ip:
            # Show arrow indicator for .replx configured WebREPL when not connected
            webrepl_lines.append(f"[dim]→[/dim] [{color}]{ip}[/{color}]")
        else:
            webrepl_lines.append(f"  [{color}]{ip}[/{color}]")

    # Build output
    output_lines = []

    # Serial section
    output_lines.append("[bold cyan]Serial:[/bold cyan]")
    if serial_lines:
        output_lines.extend(serial_lines)
    else:
        output_lines.append("  [dim]No serial devices found[/dim]")

    output_lines.append("")  # Empty line separator

    # WebREPL section
    output_lines.append("[bold cyan]WebREPL:[/bold cyan]")
    if webrepl_lines:
        output_lines.extend(webrepl_lines)
    else:
        output_lines.append("  [dim]No WebREPL devices found[/dim]")

    OutputHelper.print_panel(
        "\n".join(output_lines),
        title="MicroPython Devices",
        border_style="cyan"
    )
def main():
    # Check if replx command is run without arguments
    if len(sys.argv) == 1:
        OutputHelper.print_panel(
            f"Use [bright_blue]replx --help[/bright_blue] to see available commands.",
            title="Replx",
            border_style="green"
        )
        raise SystemExit()
    
    # Handle -v / --version
    if len(sys.argv) == 2 and sys.argv[1] in ('--version', '-v'):
        OutputHelper.print_panel(
            f"[bright_blue]replx[/bright_blue] version [bright_green]{__version__}[/bright_green]",
            title="Version",
            border_style="green"
        )
        sys.exit(0)
    
    # Handle -c / --command
    if sys.argv[1] in ('-c', '--command'):
        if len(sys.argv) < 3:
            OutputHelper.print_panel(
                "Missing required argument: [yellow]COMMAND[/yellow]\n\n"
                "[bold cyan]Usage:[/bold cyan]\n"
                "  replx -c [yellow]COMMAND[/yellow]\n\n"
                "[bold cyan]Examples:[/bold cyan]\n"
                "  replx -c \"print('hello')\"",
                title="Command Required",
                border_style="red"
            )
            sys.exit(1)
        
        # Execute the command on the device
        from ..agent.client import AgentClient
        
        command_str = sys.argv[2]
        
        try:
            _ensure_connected()
            client = AgentClient(port=_get_agent_port())
            result = client.send_command('exec', code=command_str)
            output = result.get('output', '')
            if output:
                print(output, end='')
                if not output.endswith('\n'):
                    print()
        except Exception as e:
            error_msg = str(e)
            if 'Not connected' in error_msg:
                OutputHelper.print_panel(
                    "Not connected to any device.\n\nRun [bright_green]replx connect --port COM3[/bright_green] first.",
                    title="Connection Required",
                    border_style="red"
                )
            else:
                typer.echo(f"Error: {error_msg}", err=True)
            sys.exit(1)
        sys.exit(0)
    
    # Check if replx --help is run (with only --help or -h flag)
    if len(sys.argv) == 2 and sys.argv[1] in ('--help', '-h'):
        # Show custom main help (single box)
        _print_main_help()
        sys.exit(0)

    # Normalize -ne and -en options
    try:
        out = [sys.argv[0]]
        for tok in sys.argv[1:]:
            if not tok.startswith('-') or tok.startswith('--') or len(tok) <= 2:
                out.append(tok)
                continue

            if tok in ('-ne', '-en'):
                out.extend(['-n', '-e'])
                continue

            if tok.startswith('-') and set(tok[1:]).issubset({'n', 'e'}) and len(tok) > 2:
                typer.echo("Error: Option chaining error: -n and -e can only be used once, not multiple times.", err=True)
                sys.exit(2)
            
            out.append(tok)
        sys.argv = out
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(2)

    args = sys.argv[1:]

    known = {
        "install","put","get","cat","rm","mv","cp","touch","run","format","search",
        "repl","df","shell","mkdir","ls","reset","env","scan","port","update","target","stat","mem"
    }

    first_nonopt_idx = next((i for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('-')), None)
    first_nonopt = sys.argv[first_nonopt_idx] if first_nonopt_idx is not None else None

    run_opts = {'-n', '--non-interactive', '-e', '--echo', '-d', '--device'}
    has_device_opt = bool(run_opts & {'-d', '--device'} & set(args))
    
    # Find script file: .py always, .mpy only with -d option
    script_arg_idx = next((i for i, a in enumerate(sys.argv[1:], 1) 
                          if a.endswith('.py') or (has_device_opt and a.endswith('.mpy'))), None)

    should_inject_run = (
        ('run' not in args) and
        (script_arg_idx is not None) and
        (first_nonopt is None or first_nonopt not in known)
    )

    if should_inject_run:
        opt_idx = next((i for i, a in enumerate(sys.argv[1:], 1) if a in run_opts), None)
        insert_at = opt_idx if opt_idx is not None else script_arg_idx
        sys.argv.insert(insert_at, 'run')

        first_nonopt_idx = next((i for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('-')), None)
        first_nonopt = sys.argv[first_nonopt_idx] if first_nonopt_idx is not None else None

    suppressed = {'search', 'update', 'scan', 'port'}
    if not any(x in sys.argv for x in ('--help','-h','--version','-v')):
        if (first_nonopt is None) or (first_nonopt not in suppressed):
            UpdateChecker.check_for_updates(__version__)
        
    try:
        EnvironmentManager.load_env_from_rep()
        app(standalone_mode=False)
        exit_code = 0
    except click.exceptions.UsageError as e:
        # Handle UsageError with our custom formatter
        _handle_usage_error(e)
        exit_code = 2
    except click.exceptions.Abort:
        print()
        exit_code = 1
    except KeyboardInterrupt:
        try:
            if STATE.repl_protocol:
                STATE.repl_protocol.request_interrupt()
        except Exception:
            pass
        print()
        exit_code = 130
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
