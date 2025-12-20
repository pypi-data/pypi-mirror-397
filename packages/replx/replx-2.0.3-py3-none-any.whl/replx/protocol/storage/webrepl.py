"""WebREPL Storage operations for MicroPython devices."""

from typing import Optional, List, Tuple

from ...exceptions import ProtocolError
from .base import DeviceStorage


class WebREPLStorage(DeviceStorage):
    """WebREPL connection storage manager (Friendly REPL only)."""
    
    def __init__(self, repl_protocol, core: str = "RP2350", device: str = "", device_root_fs: str = "/"):
        """Initialize WebREPL storage manager."""
        super().__init__(repl_protocol, core, device, device_root_fs)
        # Use standard ls implementation for WebREPL
        self._ls_detailed_func = self._ls_detailed_standard
        self._ls_recursive_func = self._ls_recursive_standard

    def ls_detailed(self, path: str = "/"):
        """List directory contents (Friendly REPL)."""
        return self._ls_detailed_func(path)

    def ls_recursive(self, path: str = "/"):
        """Recursively list directory contents (Friendly REPL)."""
        return self._ls_recursive_func(path)
    
    def ls(self, path: str = "/") -> list:
        """
        List directory contents (names only).
        
        :param path: Directory path
        :return: List of filenames/directory names
        """
        safe_path = path.replace("'", "\\'")
        command = f"""
import os
try:
    print(os.listdir('{safe_path}'))
except:
    print('[]')
"""
        result = self.repl.exec(command).decode('utf-8').strip()
        try:
            import ast
            return ast.literal_eval(result)
        except:
            return []
    
    def _normalize_remote_path(self, path: str) -> str:
        """Normalize a remote path."""
        if not path.startswith(self.device_root_fs):
            if path.startswith("/"):
                path = path[1:]
            import posixpath
            return posixpath.join(self.device_root_fs, path)
        return path
    
    def get(self, remote: str, local: str = None) -> bytes:
        """
        Download a file from the device.
        
        NOT SUPPORTED on WebREPL (requires Raw REPL).
        
        :raises ProtocolError: Always - operation not supported
        """
        raise ProtocolError(
            "File download (get) is not supported over WebREPL.\n"
            "WebREPL only supports Friendly REPL mode. Raw REPL (required for file transfer) is not available.\n"
            "Please use a Serial connection for file operations."
        )
    
    def put(self, local: str, remote: str, progress_callback=None):
        """
        Upload a file to the device.
        
        NOT SUPPORTED on WebREPL (requires Raw REPL).
        
        :raises ProtocolError: Always - operation not supported
        """
        raise ProtocolError(
            "File upload (put) is not supported over WebREPL.\n"
            "WebREPL only supports Friendly REPL mode. Raw REPL (required for file transfer) is not available.\n"
            "Please use a Serial connection for file operations."
        )
    
    def _ls_detailed_standard(self, dir: str = "/") -> List[list]:
        """
        List directory contents with file details via Friendly REPL.
        
        Returns: [[filename, size, is_directory], ...]
        """
        import json
        
        dir = self._normalize_remote_path(dir)
        
        command = f"""
import os
import json
items = []
try:
    for item in os.listdir('{dir}'):
        full_path = '{dir}' + ('/' if '{dir}' != '/' else '') + item
        try:
            stat_info = os.stat(full_path)
            is_dir = stat_info[0] & 0x4000 != 0
            size = 0 if is_dir else stat_info[6]
            items.append([item, size, is_dir])
        except:
            items.append([item, 0, False])
    items.sort(key=lambda x: (not x[2], x[0].lower()))
except:
    pass
print(json.dumps(items))
"""
        result = self.repl.exec(command)
        result_str = result.decode('utf-8', errors='replace') if isinstance(result, bytes) else result
        
        try:
            return json.loads(result_str)
        except (json.JSONDecodeError, ValueError):
            return []
    
    def _ls_recursive_standard(self, dir: str = "/") -> List[dict]:
        """
        Recursively list directory contents via Friendly REPL.
        
        Returns: [{"path": str, "size": int, "is_dir": bool}, ...]
        """
        import json
        
        dir = self._normalize_remote_path(dir)
        
        command = f"""
import os
import json

def walk_dir(path, base_path):
    result = []
    try:
        items = os.listdir(path)
    except:
        return result
    
    for item in items:
        full_path = path + ('/' if path != '/' else '') + item
        rel_path = base_path + ('/' if base_path else '') + item
        
        try:
            stat_info = os.stat(full_path)
            is_dir = stat_info[0] & 0x4000 != 0
            size = 0 if is_dir else stat_info[6]
            
            result.append({{"path": rel_path, "size": size, "is_dir": is_dir}})
            
            if is_dir:
                result.extend(walk_dir(full_path, rel_path))
        except:
            pass
    
    return result

items = walk_dir('{dir}', '')
print(json.dumps(items))
"""
        result = self.repl.exec(command)
        result_str = result.decode('utf-8', errors='replace') if isinstance(result, bytes) else result
        
        try:
            return json.loads(result_str)
        except (json.JSONDecodeError, ValueError):
            return []
    
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""
        path = self._normalize_remote_path(path)
        command = f"""
import os
try:
    stat_info = os.stat('{path}')
    print(1 if (stat_info[0] & 0x4000 != 0) else 0)
except:
    print(0)
"""
        result = self.repl.exec(command)
        return bool(int(result.decode('utf-8', errors='replace').strip()))
    
    def state(self, path: str) -> int:
        """Get file size."""
        path = self._normalize_remote_path(path)
        command = f"""
import os
try:
    stat_info = os.stat('{path}')
    print(stat_info[6])
except:
    print(0)
"""
        result = self.repl.exec(command)
        try:
            return int(result.decode('utf-8', errors='replace').strip())
        except:
            return 0
    
    def mkdir(self, path: str) -> bool:
        """Create directory."""
        path = self._normalize_remote_path(path)
        command = f"""
import os
try:
    os.mkdir('{path}')
    print(1)
except:
    print(0)
"""
        result = self.repl.exec(command)
        return bool(int(result.decode('utf-8', errors='replace').strip()))
    
    def rm(self, path: str):
        """Remove file."""
        path = self._normalize_remote_path(path)
        command = f"""
import os
try:
    os.remove('{path}')
except:
    pass
"""
        self.repl.exec(command)
    
    def rmdir(self, path: str):
        """Remove directory."""
        path = self._normalize_remote_path(path)
        command = f"""
import os
try:
    os.rmdir('{path}')
except:
    pass
"""
        self.repl.exec(command)
    
    def mem(self) -> Tuple[int, int, int, float]:
        """Get device memory info."""
        command = """
import gc
gc.collect()
alloc = gc.mem_alloc()
free = gc.mem_free()
total = alloc + free
pct = (alloc / total * 100) if total > 0 else 0
print(f'{alloc},{free},{total},{pct}')
"""
        result = self.repl.exec(command)
        result_str = result.decode('utf-8', errors='replace').strip()
        try:
            parts = result_str.split(',')
            return (int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3]))
        except:
            return (0, 0, 0, 0.0)
