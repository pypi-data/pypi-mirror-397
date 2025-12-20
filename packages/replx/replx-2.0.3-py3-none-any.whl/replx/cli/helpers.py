"""Helper classes for replx operations."""
import os
import sys
import re
import time
import json
import base64
import shutil
import stat
import hashlib
import urllib.request
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import typer
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED, HORIZONTALS

# Panel box style: "rounded" (4-side box) or "horizontals" (top/bottom only)
PANEL_BOX_STYLE = "rounded"  # Options: "rounded", "horizontals"
CONSOLE_WIDTH = 100  # Global console/panel width

def get_panel_box():
    """Get panel box style based on PANEL_BOX_STYLE setting."""
    return HORIZONTALS if PANEL_BOX_STYLE == "horizontals" else ROUNDED

# Import custom exceptions
try:
    from ..exceptions import CompilationError, ValidationError
except ImportError:
    # Fallback for direct module execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from exceptions import CompilationError, ValidationError


SUPPORT_CORE_DEVICE_TYPES = {
    'EFR32MG': {'xnode'}, # XBee3 Zigbee
    'RP2350': {'ticle', 'ticle-lite', 'ticle-sensor', 'xconvey', 'xhome', 'autocon'}, # Pico 2W
    'MIMXRT1062DVJ6A': {'teensy'}, # Teensy 4.0
}

# Core-specific filesystem root paths
# Some MicroPython ports use '/' as root, others use '/flash'
CORE_ROOT_FS = {
    'RP2350': '/',
    'EFR32MG': '/flash',
    'MIMXRT1062DVJ6A': '/flash',
}
DEFAULT_ROOT_FS = '/'  # Default for unknown cores


def get_root_fs_for_core(core: str) -> str:
    """Get the filesystem root path for a given core."""
    return CORE_ROOT_FS.get(core, DEFAULT_ROOT_FS)


def parse_device_banner(banner_text: str) -> Optional[Tuple[str, str, str, str]]:
    """Parse MicroPython REPL banner to extract device information."""
    import re
    
    # Extract version
    version_match = re.search(r'v(\d+\.\d+(?:\.\d+)?)', banner_text)
    version = version_match.group(1) if version_match else '?'
    
    # Extract "prefix with core" pattern
    match = re.search(r';\s*(.+?)\s+with\s+(\S+)', banner_text)
    if not match:
        return None
    
    prefix = match.group(1).strip()  # "Hanback Electronics TiCLE-Lite" or "Raspberry Pi Pico 2" or "Teensy 4.0" or "XBee3 Zigbee"
    core = match.group(2).strip().upper()  # "RP2350", "EFR32MG", "MIMXRT1062DVJ6A"
    
    # Get all known devices for this core
    device_set = SUPPORT_CORE_DEVICE_TYPES.get(core, set())
    
    # Try to find known device in prefix (case-insensitive, longest match first)
    device = None
    manufacturer = None
    
    # Sort by length descending to match longest device name first
    # e.g., "ticle-lite" before "ticle"
    for known_device in sorted(device_set, key=len, reverse=True):
        # Check if prefix ends with this device (case-insensitive)
        prefix_lower = prefix.lower()
        if prefix_lower.endswith(known_device):
            # Found known device
            device = known_device
            # Extract manufacturer (everything before device)
            idx = prefix_lower.rfind(known_device)
            manufacturer = prefix[:idx].strip()
            break
    
    if device is None:
        # Device name not found in prefix
        if len(device_set) == 1:
            # Only one device for this core - use it (e.g., EFR32MG -> xnode)
            device = next(iter(device_set))
            # manufacturer = first word of prefix (e.g., "XBee3 Zigbee" -> "XBee3")
            manufacturer = prefix.split()[0] if prefix else "Unknown"
        else:
            # Unknown device: device = core, manufacturer = entire prefix
            device = core
            manufacturer = prefix
    
    if not manufacturer:
        manufacturer = "Unknown"
    
    return version, core, device, manufacturer


# Global state variables (set by CLI in replx.py)
# These will be imported and set by replx.py main module
_core = ""
_device = ""
_version = "?"
_device_root_fs = "/"
_device_path = ""
_file_system = None


def set_global_context(core: str, device: str, version: str, device_root_fs: str, device_path: str, file_system):
    """Set global context variables used by helper classes."""
    global _core, _device, _version, _device_root_fs, _device_path, _file_system
    _core = core
    _device = device
    _version = version
    _device_root_fs = device_root_fs
    _device_path = device_path
    _file_system = file_system


class OutputHelper:
    """Output formatting and display utilities."""
    
    import sys
    import io
    # Ensure stdout uses UTF-8 encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    _console = Console()
    PANEL_WIDTH = None
    
    @staticmethod
    def _get_panel_width():
        """Get panel width."""
        if OutputHelper.PANEL_WIDTH is None:
            OutputHelper.PANEL_WIDTH = CONSOLE_WIDTH
        return OutputHelper.PANEL_WIDTH
    
    @staticmethod
    def print_panel(content: str, title: str = "", border_style: str = "blue"):
        """Print content in a rich panel box."""
        width = OutputHelper._get_panel_width()
        OutputHelper._console.print(Panel(content, title=title, title_align="left", border_style=border_style, box=get_panel_box(), expand=True, width=width))
    
    @staticmethod
    def create_progress_panel(current: int, total: int, title: str = "Progress", message: str = ""):
        """Create a progress panel for live updates with consistent width."""
        pct = 0 if total == 0 else min(1.0, current / total)
        
        # Calculate bar length based on panel width
        # Panel width - borders (4) - padding (2) - percentage text (~15) - counters (~20)
        panel_width = OutputHelper._get_panel_width()
        bar_length = max(20, panel_width - 23)  # Minimum 20 chars for bar
        
        block = min(bar_length, int(round(bar_length * pct)))
        bar = "█" * block + "░" * (bar_length - block)
        percent = int(pct * 100)
        
        content_lines = []
        if message:
            content_lines.append(message)
        content_lines.append(f"[{bar}] {percent}% ({current}/{total})")
        
        width = OutputHelper._get_panel_width()
        return Panel("\n".join(content_lines), title=title, border_style="green", box=get_panel_box(), expand=True, width=width)
    
    @staticmethod
    def create_spinner_panel(message: str, title: str = "Processing", spinner_frames: list = None, frame_idx: int = 0):
        """Create a spinner panel for indeterminate progress."""
        if spinner_frames is None:
            spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        spinner = spinner_frames[frame_idx % len(spinner_frames)]
        content = f"{spinner}  {message}"
        width = OutputHelper._get_panel_width()
        return Panel(content, title=title, border_style="yellow", box=get_panel_box(), expand=True, width=width)
    
    @staticmethod
    def print_progress_bar(current: int, total: int, bar_length: int = 40):
        """Print a progress bar to stdout."""
        pct = 0 if total == 0 else min(1.0, current / total)
        block = min(bar_length, int(round(bar_length * pct)))
        bar = "#" * block + "-" * (bar_length - block)
        percent = int(pct * 100)
        print(f"\r[{bar}] {percent}% ({current}/{total})", end="", flush=True)
    
    @staticmethod
    def format_error_output(out, local_file):
        """Process the error output from the device and print it in a readable format."""
        _error_header = b"Traceback (most recent call last):"
        
        OutputHelper._console.print(f"\r[dim]{'-'*40}Traceback{'-'*40}[/dim]")
        for l in out[1:-2]:
            if "<stdin>" in l:
                full_path = os.path.abspath(os.path.join(os.getcwd(), local_file))
                l = l.replace("<stdin>", full_path, 1)
            print(l.strip())
            
        try:
            err_line_raw = out[-2].strip()
            
            if "<stdin>" in err_line_raw:
                full_path = os.path.abspath(os.path.join(os.getcwd(), local_file))
                err_line = err_line_raw.replace("<stdin>", full_path, 1)
            else:
                match = re.search(r'File "([^"]+)"', err_line_raw)
                if match:
                    device_src_path = os.path.join(_device_path, "src")
                    full_path = os.path.join(device_src_path, match.group(1))
                    escaped_filename = re.sub(r"([\\\\])", r"\\\1", full_path)
                    err_line = re.sub(r'File "([^"]+)"', rf'File "{escaped_filename}"', err_line_raw)
                else:
                    full_path = os.path.abspath(os.path.join(os.getcwd(), local_file))
                    err_line = err_line_raw
                    
            print(f" {err_line}")
            
            err_content = out[-1].strip()

            match = re.search(r"line (\d+)", err_line)
            if match:
                line = int(match.group(1))
                try:
                    with open(full_path, "r") as f:
                        lines = f.readlines()
                        print(f"  {lines[line - 1].rstrip()}")
                except:
                    pass

        except IndexError:
            err_content = out[-1].strip()
        
        OutputHelper._console.print(f"[bright_magenta]{err_content}[/bright_magenta]")


class DeviceScanner:
    """Device detection and scanning utilities."""
    
    @staticmethod
    def get_board_info_from_banner(port: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Get device info by reading MicroPython REPL banner from serial port.
        Uses Ctrl+B to get banner text and parses it with parse_device_banner().
        
        Returns: (version, core, device, manufacturer) or None if failed
        """
        ser = None
        try:
            import serial
            # Use short timeouts to prevent blocking
            ser = serial.Serial(port, 115200, timeout=0.5, write_timeout=0.3)
            
            # Interrupt any running program and get banner
            ser.write(b'\x03\x03')  # Ctrl+C twice to ensure interrupt
            time.sleep(0.05)
            ser.reset_input_buffer()
            
            # Request banner with Ctrl+B (exit raw REPL / soft reset banner)
            ser.write(b'\x02')  # Ctrl+B
            time.sleep(0.1)
            
            # Read response
            response = b""
            start_time = time.time()
            while time.time() - start_time < 0.5:
                if ser.in_waiting:
                    response += ser.read(ser.in_waiting)
                    # Banner ends with >>> prompt
                    if b'>>>' in response:
                        break
                time.sleep(0.02)
            
            response_str = response.decode(errors='ignore')
            
            # Use common parsing function
            return parse_device_banner(response_str)
                        
        except Exception:
            # Any error (serial, timeout, etc.) - skip this port
            pass
        finally:
            if ser:
                try:
                    ser.close()
                except:
                    pass
        
        return None
    
    @staticmethod
    def scan_serial_ports(max_workers: int = 5, exclude_port: str = None) -> list:
        """
        Scan all available serial ports in parallel using banner detection.
        
        Returns list of tuples: (port_device, board_info)
        where board_info is (version, core, device, manufacturer)
        
        Uses ThreadPoolExecutor for parallel scanning - much faster than sequential.
        Typical time: 1-2 seconds (vs 10-20 seconds sequential)
        
        :param max_workers: Number of parallel threads (default 5)
        :param exclude_port: Port to exclude from scanning (e.g., agent-connected port)
        :return: List of (port_device, board_info) tuples for connected boards
        """
        from serial.tools.list_ports import comports as list_ports_comports
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        # Get list of valid serial ports (excluding Bluetooth and excluded port)
        valid_ports = []
        for port in list_ports_comports():
            if DeviceScanner.is_bluetooth_port(port):
                continue
            # Exclude agent-connected port (case-insensitive for Windows)
            if exclude_port and port.device.upper() == exclude_port.upper():
                continue
            valid_ports.append(port)
        
        if not valid_ports:
            return results
        
        # Parallel scan using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all port scans using banner-based detection
            future_to_port = {
                executor.submit(DeviceScanner.get_board_info_from_banner, port.device): port.device
                for port in valid_ports
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_port):
                port_device = future_to_port[future]
                try:
                    board_info = future.result(timeout=2)  # 2 second timeout per port
                    if board_info:
                        results.append((port_device, board_info))
                except Exception:
                    # Port scan timeout or error - skip this port
                    pass
        
        return results
    
    @staticmethod
    def is_bluetooth_port(port_info) -> bool:
        """Check if the given port_info is a Bluetooth port."""
        bt_keywords = ['bluetooth', 'bth', 'devb', 'rfcomm', 'blue', 'bt']
        description = port_info.description.lower()
        device = port_info.device.lower()
        return any(keyword in description or keyword in device for keyword in bt_keywords)
    
    @staticmethod
    def is_valid_serial_port(port_name: str) -> bool:
        """Check if the port_name is valid on the current platform."""
        _plat = sys.platform

        if _plat.startswith("win"):
            return re.fullmatch(r"COM[1-9][0-9]*", port_name, re.IGNORECASE) is not None
        elif _plat.startswith("linux"):
            return (
                re.fullmatch(r"/dev/tty(USB|ACM|AMA)[0-9]+", port_name) is not None or
                port_name.startswith("/dev/serial/by-id/")
            )
        elif _plat == "darwin":
            return re.fullmatch(r"/dev/(tty|cu)\..+", port_name) is not None
        return False


class DeviceValidator:
    """Device and core validation utilities."""
    
    @staticmethod
    def find_core_by_device(device_name: str) -> Optional[str]:
        """Find core type by device name."""
        for core, devices in SUPPORT_CORE_DEVICE_TYPES.items():
            if device_name in devices:
                return core
        return None
    
    @staticmethod
    def is_supported_core(core: str) -> bool:
        """Check if core type is supported."""
        return core in SUPPORT_CORE_DEVICE_TYPES
    
    @staticmethod
    def is_supported_device(device: str) -> bool:
        """Check if device is supported."""
        all_devices = set()
        for devices in SUPPORT_CORE_DEVICE_TYPES.values():
            all_devices.update(devices)
        return device in all_devices


class NetworkScanner:
    """Network scanning utilities for WebREPL discovery."""
    
    WEBREPL_PORT = 8266
    PORT_SCAN_TIMEOUT = 0.1  # seconds per port (100ms - shorter timeout for faster scanning)
    REPL_READ_TIMEOUT = 0.5  # seconds for reading device info
    
    @staticmethod
    def get_local_ip():
        """Get the local IP address of the PC."""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to a public DNS (doesn't actually send packets)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None
    
    @staticmethod
    def get_subnet_mask(ip_address: str):
        """Get the subnet mask for a given IP address."""
        try:
            import socket
            import struct
            
            # Try to get subnet mask from platform-specific methods
            if sys.platform.startswith('win'):
                import subprocess
                result = subprocess.run(
                    ['ipconfig'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.split('\n')
                ip_line_idx = None
                
                # Find the line with our IP
                for i, line in enumerate(lines):
                    if ip_address in line:
                        ip_line_idx = i
                        break
                
                if ip_line_idx:
                    # Look for subnet mask near the IP line
                    for i in range(max(0, ip_line_idx - 5), min(len(lines), ip_line_idx + 5)):
                        if 'Subnet Mask' in lines[i]:
                            mask = lines[i].split(':')[1].strip()
                            return mask
            else:
                # Unix-like systems
                import subprocess
                result = subprocess.run(
                    ['ifconfig'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.split('\n')
                
                for i, line in enumerate(lines):
                    if ip_address in line and 'inet' in line:
                        # Look for netmask in the same or next line
                        for j in range(i, min(len(lines), i + 3)):
                            if 'netmask' in lines[j]:
                                parts = lines[j].split()
                                for k, part in enumerate(parts):
                                    if part == 'netmask':
                                        mask_hex = parts[k + 1]
                                        # Convert hex netmask to dotted decimal
                                        mask_int = int(mask_hex, 16)
                                        mask = '.'.join([str((mask_int >> (8 * (3 - i))) & 0xff) for i in range(4)])
                                        return mask
            
            # Default to /24 if detection fails
            return "255.255.255.0"
        except Exception:
            return "255.255.255.0"
    
    @staticmethod
    def ip_to_int(ip: str):
        """Convert IP address string to integer."""
        import socket
        return int(socket.inet_aton(ip).hex(), 16)
    
    @staticmethod
    def int_to_ip(ip_int: int):
        """Convert integer to IP address string."""
        return '.'.join([str((ip_int >> (8 * (3 - i))) & 0xff) for i in range(4)])
    
    @staticmethod
    def get_network_ips(local_ip: str, subnet_mask: str):
        """Get all usable IPs in the network (excluding network, broadcast, and local IP)."""
        import socket
        
        # Convert to integers
        ip_int = NetworkScanner.ip_to_int(local_ip)
        mask_int = NetworkScanner.ip_to_int(subnet_mask)
        
        # Calculate network and broadcast addresses
        network_int = ip_int & mask_int
        broadcast_int = network_int | (~mask_int & 0xffffffff)
        
        # Generate all IPs in range (excluding network, broadcast, and local IP)
        ips = []
        for i in range(network_int + 1, broadcast_int):
            if i != ip_int:  # Exclude local IP
                ips.append(NetworkScanner.int_to_ip(i))
        
        return ips
    
    @staticmethod
    def is_port_open(host: str, port: int = WEBREPL_PORT, timeout: float = PORT_SCAN_TIMEOUT) -> bool:
        """Check if a port is open on a host (non-blocking)."""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except Exception:
            return False
        finally:
            sock.close()
    
    @staticmethod
    def get_webrepl_info(host: str, password: str = "", timeout: float = REPL_READ_TIMEOUT) -> Optional[Tuple[str, str, str, str]]:
        """
        Get WebREPL device information (version, date, core, device).
        For scan purposes, we just verify the WebREPL connection works.
        
        Returns: (version, date, core, device) or None if failed
        """
        import threading
        
        info = [None]
        
        def connect_and_get_info():
            """Connect and retrieve device info in a thread with timeout."""
            try:
                # Dynamically import transport factory
                from ..transport import create_transport
                
                transport = create_transport(
                    f"ws://{host}:{NetworkScanner.WEBREPL_PORT}",
                    password=password,
                    timeout=timeout
                )
                
                # Send command to get device info
                cmd = b"import sys; print(sys.implementation.version[:3], end=' '); print(sys.platform)\r\n"
                transport.write(cmd)
                
                # Read response with timeout
                response = b""
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        chunk = transport.read_available(timeout_ms=50)
                        if chunk:
                            response += chunk
                            if b'\n' in response or b'>>>' in response:
                                break
                    except Exception:
                        break
                    time.sleep(0.01)
                
                transport.close()
                
                # Parse response
                response_str = response.decode('utf-8', errors='ignore').strip()
                if response_str:
                    info[0] = parse_device_banner(response_str)
            except Exception:
                # Connection failed or timeout
                pass
        
        # Run connection in thread with hard timeout
        thread = threading.Thread(target=connect_and_get_info, daemon=True)
        thread.start()
        thread.join(timeout=timeout + 1.0)  # Add 1 second buffer
        
        return info[0]
    
    @staticmethod
    def scan_webrepl_network(max_workers: int = 10, show_progress: bool = False) -> list:
        """
        Scan for WebREPL devices on the local network.
        
        Process:
        1. Get local IP and subnet mask
        2. Generate all usable IPs in the subnet (excluding network, broadcast, local)
        3. Port scan for open port 8266
        4. For each open port, try to read device info
        
        Returns: List of tuples (ip_address, device_info)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Step 1: Get local IP
        local_ip = NetworkScanner.get_local_ip()
        if not local_ip:
            return []
        
        # Step 2: Get subnet mask
        subnet_mask = NetworkScanner.get_subnet_mask(local_ip)
        
        # Step 3: Get all usable IPs
        all_ips = NetworkScanner.get_network_ips(local_ip, subnet_mask)
        if not all_ips:
            return []
        
        results = []
        
        # Step 4: Parallel port scan
        open_ports = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(NetworkScanner.is_port_open, ip): ip
                for ip in all_ips
            }
            
            for future in as_completed(futures):
                ip = futures[future]
                try:
                    if future.result():
                        open_ports.append(ip)
                except Exception:
                    pass
        
        # Step 5: For each open WebREPL port, add as detected device
        # (We don't attempt to get device info during scan - just detect presence)
        for ip in open_ports:
            results.append((ip, "WebREPL"))
        
        return results


class EnvironmentManager:
    """Environment setup and file management utilities."""
    
    @staticmethod
    def load_env_from_rep():
        """Load environment variables from the .replx file in the .vscode directory."""
        current_path = os.getcwd()

        while True:
            min_path = os.path.join(current_path, ".vscode", ".replx")
            if os.path.isfile(min_path):
                with open(min_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
                return
            
            parent_path = os.path.dirname(current_path)
            if parent_path == current_path:
                return
            current_path = parent_path
    
    @staticmethod
    def copy_tree_or_file(src: str, dst: str) -> None:
        """Copy a file or directory tree."""
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst, onerror=EnvironmentManager.force_remove_readonly)
            shutil.copytree(src, dst)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    
    @staticmethod
    def link_typehints_into_vscode(src_dir: str, vscode_dir: str, subdir: str = None) -> int:
        """Link typehints directory into .vscode.
        
        Flattens ext/<domain>/<target>/*.pyi to ext/*.pyi for deployment compatibility.
        
        :param src_dir: Source directory containing typehints
        :param vscode_dir: Target .vscode directory
        :param subdir: Optional subdirectory name to create under vscode_dir
        :return: Number of files/folders copied
        """
        if not os.path.isdir(src_dir):
            return 0

        # If subdir is specified, create target directory under vscode_dir
        if subdir:
            target_dir = os.path.join(vscode_dir, subdir)
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = vscode_dir

        n = 0
        micropython_dir = None
        ext_dir = None
        
        # First pass: copy all files/folders except 'micropython' and 'ext'
        for name in os.listdir(src_dir):
            s = os.path.join(src_dir, name)
            
            # Skip 'micropython' folder in first pass
            if name == "micropython" and os.path.isdir(s):
                micropython_dir = s
                continue
            
            # Skip 'ext' folder in first pass (handle separately)
            if name == "ext" and os.path.isdir(s):
                ext_dir = s
                continue
            
            d = os.path.join(target_dir, name)
            EnvironmentManager.copy_tree_or_file(s, d)
            n += 1
        
        # Second pass: copy contents of 'micropython' folder directly into target_dir
        if micropython_dir:
            for name in os.listdir(micropython_dir):
                s = os.path.join(micropython_dir, name)
                d = os.path.join(target_dir, name)
                EnvironmentManager.copy_tree_or_file(s, d)
                n += 1
        
        # Third pass: flatten ext/<domain>/<target>/*.pyi to ext/*.pyi
        if ext_dir:
            ext_target = os.path.join(target_dir, "ext")
            os.makedirs(ext_target, exist_ok=True)
            
            # Copy non-domain files first (e.g., nb_impl.pyi, __init__.pyi)
            for name in os.listdir(ext_dir):
                src_path = os.path.join(ext_dir, name)
                if os.path.isfile(src_path) and name.endswith('.pyi'):
                    dst_path = os.path.join(ext_target, name)
                    shutil.copy2(src_path, dst_path)
                    n += 1
            
            # Flatten domain folders
            for domain_name in os.listdir(ext_dir):
                domain_path = os.path.join(ext_dir, domain_name)
                if not os.path.isdir(domain_path):
                    continue
                
                # Iterate through target folders in each domain
                for target_name in os.listdir(domain_path):
                    target_path = os.path.join(domain_path, target_name)
                    if not os.path.isdir(target_path):
                        continue
                    
                    # Copy all .pyi files from target folder to flat ext/ folder
                    for file_name in os.listdir(target_path):
                        if file_name.endswith('.pyi'):
                            src_file = os.path.join(target_path, file_name)
                            dst_file = os.path.join(ext_target, file_name)
                            shutil.copy2(src_file, dst_file)
                            n += 1
        
        return n
    
    @staticmethod
    def force_remove_readonly(func, path, exc_info):
        """Force remove a read-only file or directory."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"Deletion failed: {path}, error: {e}")


class StoreManager:
    """Local and remote store management utilities."""
    
    HOME_STORE = Path.home() / ".replx"
    HOME_STAGING = HOME_STORE / ".staging"
    META_NAME = "replx_registry.json"
    
    @staticmethod
    def ensure_home_store():
        """Ensure home store directories exist."""
        StoreManager.HOME_STORE.mkdir(parents=True, exist_ok=True)
        (StoreManager.HOME_STORE / "core").mkdir(exist_ok=True)
        (StoreManager.HOME_STORE / "device").mkdir(exist_ok=True)
        StoreManager.HOME_STAGING.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def pkg_root() -> str:
        """Get the package root directory."""
        StoreManager.ensure_home_store()
        return str(StoreManager.HOME_STORE)
    
    @staticmethod
    def local_meta_path() -> str:
        """Get the local metadata file path."""
        return os.path.join(StoreManager.pkg_root(), StoreManager.META_NAME)
    
    @staticmethod
    def gh_headers() -> dict:
        """Get GitHub API headers."""
        hdrs = {"User-Agent": "replx"}
        tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if tok:
            hdrs["Authorization"] = f"Bearer {tok}"
        return hdrs
    
    @staticmethod
    def load_local_meta() -> dict:
        """Load local metadata."""
        p = StoreManager.local_meta_path()
        if not os.path.exists(p):
            return {"targets": {}, "items": {}}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"targets": {}, "items": {}}
    
    @staticmethod
    def save_local_meta(meta: dict):
        """Save local metadata."""
        p = StoreManager.local_meta_path()
        tmp = p + ".tmp"
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
    
    @staticmethod
    def load_remote_meta(owner: str, repo: str, ref_: str) -> dict:
        """Load remote metadata from GitHub."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{StoreManager.META_NAME}?ref={ref_}"
        req = urllib.request.Request(url, headers=StoreManager.gh_headers())
        with urllib.request.urlopen(req) as r:
            data = json.load(r)
        b64 = (data.get("content") or "").replace("\n", "")
        if not b64:
            raise typer.BadParameter("Remote meta has no content.")
        txt = base64.b64decode(b64.encode("utf-8")).decode("utf-8")
        return json.loads(txt)
    
    @staticmethod
    def refresh_meta_if_online(owner: str, repo: str, ref_: str) -> bool:
        """Refresh metadata from online if available."""
        try:
            remote = StoreManager.load_remote_meta(owner, repo, ref_)
            StoreManager.save_local_meta(remote)
            return True
        except Exception:
            return False


class CompilerHelper:
    """MPY compilation utilities with intelligent caching."""
    
    # Cache mapping: {(abs_py, arch_tag): (file_hash, out_mpy_path)}
    _compile_cache = {}
    
    @staticmethod
    def mpy_arch_tag() -> str:
        """Get the MPY architecture tag."""
        return _core or "unknown"
    
    @staticmethod
    def staging_out_for(abs_py: str, base: str, arch_tag: str) -> str:
        """Get the staging output path for a compiled file."""
        rel = os.path.relpath(abs_py, base).replace("\\", "/")
        rel_mpy = os.path.splitext(rel)[0] + ".mpy"
        out_path = StoreManager.HOME_STAGING / arch_tag / rel_mpy
        out_path.parent.mkdir(parents=True, exist_ok=True)
        return str(out_path)
    
    @staticmethod
    def _compute_file_hash(filepath: str) -> str:
        """Compute MD5 hash of file contents for cache validation."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def compile_to_staging(abs_py: str, base: str) -> str:
        """
        Compile a Python file to MPY and stage it.
        Uses intelligent caching to skip recompilation if source hasn't changed.
        Provides 20-50% speedup for repeated installations.
        """
        # Verify source file exists
        if not os.path.exists(abs_py):
            raise ValidationError(f"Source file not found: {abs_py}")
        
        arch_tag = CompilerHelper.mpy_arch_tag()
        out_mpy = CompilerHelper.staging_out_for(abs_py, base, arch_tag)
        
        # Check cache: if output exists and source hasn't changed, skip compilation
        cache_key = (abs_py, arch_tag)
        current_hash = CompilerHelper._compute_file_hash(abs_py)
        
        if cache_key in CompilerHelper._compile_cache:
            cached_hash, cached_out = CompilerHelper._compile_cache[cache_key]
            if cached_hash == current_hash and os.path.exists(cached_out) and os.path.getsize(cached_out) > 0:
                # Cache hit! Skip compilation
                return cached_out
        
        # Cache miss or file changed - compile
        args = ['_filepath_', '-o', '_outpath_', '-msmall-int-bits=31']
        if _core == "EFR32MG":
            # Parse version string (e.g., "1.19.0") to float for comparison
            try:
                ver_parts = _version.split('.')
                ver_float = float(f"{ver_parts[0]}.{ver_parts[1]}" if len(ver_parts) >= 2 else _version)
            except (ValueError, IndexError):
                ver_float = 0.0
            if ver_float < 1.19:
                args.append('-mno-unicode')
        elif _core == "ESP32":
            args.append('-march=xtensa')
        elif _core == "ESP32S3":
            args.append('-march=xtensawin')
        elif _core == "RP2350":
            args.append('-march=armv7emsp')
        else:
            raise typer.BadParameter(f"The {_core} is not supported")
        
        # Ensure output directory exists
        out_dir = os.path.dirname(out_mpy)
        os.makedirs(out_dir, exist_ok=True)
        
        args[0] = abs_py
        args[2] = out_mpy
        
        try:
            import mpy_cross
            mpy_cross.run(*args)
        except Exception as e:
            raise CompilationError(f"MPY compilation failed for {abs_py}: {e}")
        
        # Ensure file is fully written and wait a bit for filesystem
        import time
        for _ in range(10):  # Try for 1 second
            if os.path.exists(out_mpy) and os.path.getsize(out_mpy) > 0:
                # Update cache with new compilation
                CompilerHelper._compile_cache[cache_key] = (current_hash, out_mpy)
                return out_mpy
            time.sleep(0.1)
        
        raise CompilationError(f"Compilation failed: {out_mpy} not found or empty")


class InstallHelper:
    """Installation utilities."""
    
    @staticmethod
    def is_url(s: str) -> bool:
        """Check if string is a valid URL."""
        try:
            u = urlparse(s)
            return u.scheme in ("http", "https") and bool(u.netloc) and bool(u.path)
        except Exception:
            return False
    
    @staticmethod
    def resolve_spec(spec: str) -> Tuple[str, str]:
        """Resolve a spec string to scope and rest."""
        if spec == "core":
            return "core", ""
        if spec == "device":
            return "device", ""
        if spec.startswith("core/"):
            return "core", spec[len("core/"):]
        if spec.startswith("device/"):
            return "device", spec[len("device/"):]
        raise typer.BadParameter(
            f"Invalid spec: {spec} (expect 'core[/...]' or 'device[/...]')"
        )
    
    @staticmethod
    def download_raw_file(owner: str, repo: str, ref_: str, path: str, out_path: str) -> str:
        """Download a raw file from GitHub."""
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref_}/{path}"
        req = urllib.request.Request(url, headers=StoreManager.gh_headers())
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with urllib.request.urlopen(req) as r, open(out_path, "wb") as f:
            f.write(r.read())
        return out_path
    
    @staticmethod
    def ensure_remote_dir(remote_dir: str):
        """Ensure remote directory exists on device using agent."""
        if not remote_dir:
            return
        from ..agent import AgentClient
        client = AgentClient()
        parts = [p for p in remote_dir.replace("\\", "/").strip("/").split("/") if p]
        path = _device_root_fs
        for p in parts:
            path = path + p + "/"
            try:
                client.send_command('mkdir', path=path.rstrip('/'))
            except Exception:
                pass  # Directory may already exist
    
    @staticmethod
    def remote_dir_for(scope: str, rel_dir: str) -> str:
        """Get the remote directory for a given scope."""
        if scope == "core":
            return "lib/" + (rel_dir + "/" if rel_dir else "")
        else:
            return f"lib/{_device}/" + (rel_dir + "/" if rel_dir else "")
    
    @staticmethod
    def list_local_py_targets(scope: str, rest: str) -> Tuple[str, list]:
        """List local Python targets for installation."""
        if scope == "core":
            base = os.path.join(StoreManager.pkg_root(), "core", _core, "src")
        else:
            base = os.path.join(StoreManager.pkg_root(), "device", _device, "src")

        target_path = os.path.join(base, rest)
        if os.path.isfile(target_path) and target_path.endswith(".py"):
            rel = os.path.relpath(target_path, base).replace("\\", "/")
            return base, [(target_path, rel)]

        if os.path.isdir(target_path):
            out = []
            for dp, _, fns in os.walk(target_path):
                for fn in fns:
                    if not fn.endswith(".py"):
                        continue
                    ap = os.path.join(dp, fn)
                    rel = os.path.relpath(ap, base).replace("\\", "/")
                    out.append((ap, rel))
            return base, out
        return base, []
    
    @staticmethod
    def local_store_ready_for_full_install(core: str, device: str) -> Tuple[bool, str]:
        """Check if local store is ready for full installation."""
        StoreManager.ensure_home_store()
        meta_path = StoreManager.local_meta_path()
        if not os.path.isfile(meta_path):
            return False, "meta-missing"

        try:
            _ = StoreManager.load_local_meta()
        except Exception:
            return False, "meta-broken"

        req_dirs = [
            os.path.join(StoreManager.pkg_root(), "core", core, "src"),
            os.path.join(StoreManager.pkg_root(), "core", core, "typehints"),
            os.path.join(StoreManager.pkg_root(), "device", device, "src"),
            os.path.join(StoreManager.pkg_root(), "device", device, "typehints"),
        ]
        missing = [p for p in req_dirs if not os.path.isdir(p)]
        if missing:
            return False, "dirs-missing"

        return True, "ok"


class SearchHelper:
    """Registry search utilities."""
    
    @staticmethod
    def fmt_ver_with_star(remote_ver: float, local_ver: float, missing_local: bool) -> str:
        """Format version with star if update available."""
        star = "*" if missing_local or (remote_ver > (local_ver or 0.0)) else ""
        return f"{remote_ver:.1f}{star}"
    
    @staticmethod
    def key_ci(d: dict, name: str) -> Optional[str]:
        """Case-insensitive key lookup."""
        if not isinstance(d, dict) or not name:
            return None
        if name in d:
            return name
        n = name.lower()
        for k in d.keys():
            if isinstance(k, str) and k.lower() == n:
                return k
        return None


class UpdateChecker:
    """Update checking utilities."""
    
    UPDATE_TIMESTAMP_FILE = StoreManager.HOME_STORE / "update_check"
    UPDATE_INTERVAL = int(os.environ.get("REPLX_UPDATE_INTERVAL_SEC", str(60 * 60 * 24)))
    ENV_NO_UPDATE = "REPLX_NO_UPDATE_CHECK"
    
    @staticmethod
    def is_interactive_tty() -> bool:
        """Check if running in interactive TTY."""
        try:
            return sys.stdin.isatty() and sys.stdout.isatty()
        except Exception:
            return False
    
    @staticmethod
    def check_for_updates(current_version: str, *, force: bool = False):
        """Check PyPI for a newer version of replx and prompt the user to upgrade."""
        if os.environ.get(UpdateChecker.ENV_NO_UPDATE, "").strip():
            return
        if not force and not UpdateChecker.is_interactive_tty():
            return
        
        StoreManager.ensure_home_store()
        p = UpdateChecker.UPDATE_TIMESTAMP_FILE
        try:
            should_check = (not p.exists()) or (time.time() - p.stat().st_mtime) >= UpdateChecker.UPDATE_INTERVAL
        except Exception:
            should_check = True
        
        if not should_check:
            return
        
        def _vt(v: str) -> tuple:
            parts = re.findall(r"\d+", str(v))
            return tuple(int(p) for p in parts[:3]) or (0,)

        def _is_newer(latest: str, current: str) -> bool:
            try:
                from packaging.version import Version
                return Version(str(latest)) > Version(str(current))
            except Exception:
                return _vt(latest) > _vt(current)

        try:
            with urllib.request.urlopen("https://pypi.org/pypi/replx/json", timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            latest_version = data["info"]["version"]

            if _is_newer(latest_version, current_version):
                if UpdateChecker.is_interactive_tty():
                    print(f"\n[bright_yellow]New version available: {latest_version}[/bright_yellow]")
                    print(f"Run: [bright_blue]pip install --upgrade replx[/bright_blue]\n")
        except Exception:
            pass
        finally:
            try:
                StoreManager.ensure_home_store()
                UpdateChecker.UPDATE_TIMESTAMP_FILE.touch()
            except Exception:
                pass


class RegistryHelper:
    """Helper class for managing registry metadata operations."""
    
    @staticmethod
    def root_sections(reg: dict):
        """Return (cores_dict, devices_dict) from either new or old layouts."""
        items = reg.get("items") or {}
        cores = items.get("core") or reg.get("cores") or {}
        devices = items.get("device") or reg.get("devices") or {}
        return cores, devices

    @staticmethod
    def get_node(reg: dict, scope: str, target: str) -> dict:
        cores, devices = RegistryHelper.root_sections(reg)
        if scope == "core":
            return cores.get(target, {}) or {}
        else:
            return devices.get(target, {}) or {}

    @staticmethod
    def find_entry(node: dict, name: str):
        """
        Find entry named `name` in node["files"] for list or dict layouts.
        Returns the entry object (dict or empty dict for plain file), or None.
        """
        files = node.get("files")
        if files is None:
            return None
        # Older dict layout
        if isinstance(files, dict):
            return files.get(name)
        # New list layout
        for e in files:
            if isinstance(e, str):
                if e == name:
                    return {}  # plain file (no per-file meta)
            elif isinstance(e, dict) and e.get("name") == name:
                return e
        return None

    @staticmethod
    def walk_files(node: dict, prefix: str = ""):
        """
        Yield (relpath, leaf_meta_dict) for every file under this node.
        Supports list-based and dict-based 'files'.
        """
        files = node.get("files")
        if not files:
            return
        # dict layout (old)
        if isinstance(files, dict):
            for name, meta in files.items():
                if isinstance(meta, dict) and "files" in meta:  # folder
                    yield from RegistryHelper.walk_files(meta, f"{prefix}{name}/")
                else:  # file
                    yield (f"{prefix}{name}", meta if isinstance(meta, dict) else {})
            return
        # list layout (new)
        for entry in files:
            if isinstance(entry, str):  # file
                yield (f"{prefix}{entry}", {})
            elif isinstance(entry, dict):
                nm = entry.get("name")
                if not nm:
                    continue
                if "files" in entry:     # folder
                    yield from RegistryHelper.walk_files(entry, f"{prefix}{nm}/")
                else:                    # file object with optional ver
                    yield (f"{prefix}{nm}", {"ver": entry.get("ver")})

    @staticmethod
    def get_version(d: dict, key_primary="ver", key_fallback="version", default=0.0):
        """Extract version from dict, trying primary then fallback key."""
        v = d.get(key_primary, d.get(key_fallback, default)) if isinstance(d, dict) else default
        try:
            return float(v)
        except Exception:
            return default

    @staticmethod
    def effective_version(reg: dict, scope: str, target: str, part: str, relpath: str) -> float:
        """
        Version resolution (file > nearest folder > part(ver) > node(ver) > 0.0).
        Uses 'ver' if present (falls back to 'version' just in case).
        """
        node = RegistryHelper.get_node(reg, scope, target)
        node_ver = RegistryHelper.get_version(node, default=0.0)

        part_node = (node.get(part) or {})
        part_ver = RegistryHelper.get_version(part_node, default=node_ver)

        nearest = part_ver
        if relpath:
            segs = relpath.split("/")
            dirs, leaf = segs[:-1], segs[-1]

            cur = part_node
            for d in dirs:
                ent = RegistryHelper.find_entry(cur, d)
                if not isinstance(ent, dict):
                    break
                v = RegistryHelper.get_version(ent, default=None)
                if v is not None:
                    nearest = v
                cur = ent

            # file-level override
            leaf_ent = RegistryHelper.find_entry(cur, leaf)
            if isinstance(leaf_ent, dict):
                v = RegistryHelper.get_version(leaf_ent, default=None)
                if v is not None:
                    nearest = v

        return nearest
