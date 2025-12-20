"""Serial (USB/UART) Storage operations for MicroPython devices."""
import os
import sys
import ast
import json
import textwrap
import posixpath
from typing import Tuple

from ...exceptions import ProtocolError
from .base import DeviceStorage


class SerialStorage(DeviceStorage):
    """Serial connection storage manager using Raw REPL."""
    
    _PUT_BATCH_BYTES = 16 * 1024
    _DEVICE_CHUNK_SIZES = 4096
    
    def __init__(self, repl_protocol, core: str = "RP2350", device: str = "", device_root_fs: str = "/"):
        """Initialize Serial storage manager."""
        super().__init__(repl_protocol, core, device, device_root_fs)
        self.is_webrepl = False  # Explicit marker for serial transport
        
        # Choose platform-specific listing handlers
        if device == "xnode":  # XBee device
            self._ls_detailed_func = self._ls_detailed_xbee
            self._ls_recursive_func = self._ls_recursive_xbee
        else:  # Standard platforms
            self._ls_detailed_func = self._ls_detailed_standard
            self._ls_recursive_func = self._ls_recursive_standard

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

    def ls_detailed(self, path: str = "/"):
        """List directory with details using the selected platform handler."""
        return self._ls_detailed_func(path)

    def ls_recursive(self, path: str = "/"):
        """Recursively list directory using the selected platform handler."""
        return self._ls_recursive_func(path)
    
    def _normalize_remote_path(self, path: str) -> str:
        """
        Normalize a remote path to ensure it starts with device_root_fs.
        :param path: The path to normalize.
        :return: Normalized path.
        """
        if not path.startswith(self.device_root_fs):
            if path.startswith("/"):
                path = path[1:]
            return posixpath.join(self.device_root_fs, path)
        return path
    
    def _print_progress_bar(self, current: int, total: int, bar_length: int = 40):
        """
        Print a progress bar.
        :param current: Current progress value.
        :param total: Total value.
        :param bar_length: Length of the progress bar.
        """
        pct = 0 if total == 0 else min(1.0, current / total)
        block = min(bar_length, int(round(bar_length * pct)))
        bar = "#" * block + "-" * (bar_length - block)
        percent = int(pct * 100)
        print(f"\r[{bar}] {percent}% ({current}/{total})", end="", flush=True)
    
    def _file_exists(self, path: str) -> bool:
        """Check if a file exists on the device."""
        safe_path = path.replace("'", "\\'")
        command = f"""
import os
try:
    os.stat('{safe_path}')
    print('1')
except:
    print('0')
"""
        result = self.repl.exec(command).decode('utf-8').strip()
        return result == '1'
    
    def get(self, remote: str, local: str = None) -> bytes:
        """
        Download a file from the connected device.
        
        NOTE: WebREPL (Friendly REPL only) does not support file downloads due to
        lack of Raw REPL support. This method only works with Serial connections.
        
        Uses base64 encoding to safely transfer binary files through REPL.
        
        :param remote: The path to the file on the device.
        :param local: The local path where the file should be saved.
                      If None, returns file content as bytes.
        :return: File content as bytes if local is None, otherwise None.
        :raises ProtocolError: If the file doesn't exist or download fails.
        """
        if self.is_webrepl:
            raise ProtocolError("File download (get) is not supported over WebREPL. Use Serial connection instead.")
        
        import binascii as binascii_module
        
        local_file = None
        content_parts = []  # For returning content when local is None
        
        if local:
            if os.path.isdir(local):
                local = os.path.join(local, os.path.basename(remote))
            local_file = open(local, "wb")
        
        bytes_read = 0

        try:
            file_size = self.state(remote)
            
            # Check if file exists (size 0 could be empty file or non-existent)
            if file_size == 0:
                if not self._file_exists(remote):
                    raise ProtocolError(f"File not found: {remote}")
                # File exists but is empty
                return b"" if not local else None

            with self.repl.session():
                # Use base64 encoding to safely transfer binary data through REPL
                init_command = f"""
                    import sys
                    import binascii
                    f = open('{remote}', 'rb')
                    """
                self.repl._exec(textwrap.dedent(init_command))
                
                CHUNK_SIZE = 12288  # 12KB chunks (becomes ~16KB after base64)
                
                while bytes_read < file_size:
                    remaining = min(CHUNK_SIZE, file_size - bytes_read)

                    read_cmd = f"""
                        chunk = f.read({remaining})
                        if chunk:
                            encoded = binascii.b2a_base64(chunk)
                            sys.stdout.write(encoded.decode('ascii'))
                        """
                    encoded_data = self.repl._exec(textwrap.dedent(read_cmd))
                    
                    if encoded_data:
                        try:
                            chunk_data = binascii_module.a2b_base64(encoded_data)
                        except Exception as e:
                            raise ProtocolError(f"Failed to decode base64 data: {e}")
                        
                        if local_file:
                            local_file.write(chunk_data)
                        else:
                            content_parts.append(chunk_data)
                    
                        bytes_read += len(chunk_data)
                    else:
                        break

                self.repl._exec("f.close()")
        
        except ProtocolError:
            raise
        except Exception as e:
            raise ProtocolError(f"Download failed: {e}")
        finally:
            if local_file:
                local_file.close()

        if bytes_read != file_size:
            raise ProtocolError(f"Download incomplete: got {bytes_read}/{file_size} bytes")
        
        # Return content if no local path specified
        if not local:
            return b''.join(content_parts)
    
    def state(self, path: str) -> int:
        """
        Return file size of given path.
        Returns 0 if file doesn't exist or on error.
        """
        if self.core == "EFR32MG":
            command = f"""
                try:
                    with open('{path}', 'rb') as f:
                        f.seek(0, 2)
                        size = f.tell()
                    print(size)
                except:
                    print(0)
            """
            out = self.repl.exec(command)
            result = out.decode('utf-8').strip()
            try:
                return int(result)
            except ValueError:
                return 0
        else:
            # Escape single quotes in path for Python command
            safe_path = path.replace("'", "\\'")
            command = f"""
                import os
                try:
                    st = os.stat('{safe_path}')
                    print(st[6])
                except:
                    print(0)
            """
            out = self.repl.exec(command)
            result = out.decode('utf-8').strip()
            try:
                return int(result)
            except ValueError:
                return 0
    
    def is_dir(self, path: str) -> bool:
        """
        Check if the given path is a directory.
        :param path: The path to check.
        :return: True if the path is a directory, False otherwise.
        """
        command = f"""
try:
    from os import stat
    result = stat('{path}')[0] & 0x4000 != 0
except ImportError:
    from os import listdir
    try:
        listdir('{path}')
        result = True
    except OSError:
        result = False
print(result)
        """
        out = self.repl.exec(command)
        return ast.literal_eval(out.decode("utf-8"))
    
    def _ls_detailed_xbee(self, dir: str = "/") -> list:
        """
        XBee-specific ls implementation (no stat() support).
        Uses file open + seek to determine size.
        """
        if not dir.startswith("/"):
            dir = "/" + dir
        
        command = f"""
            import os
            import json
            def xbee3_zigbee_state(path):
                try:
                    with open(path, 'rb') as f:
                        f.seek(0, 2)
                        size = f.tell()
                    return size
                except Exception as e:
                    return 0

            def get_detailed_listing(path):
                try:
                    items = []
                    for item in os.listdir(path):
                        full_path = path + ('/' + item if path != '/' else item)
                        is_dir = False
                        size = xbee3_zigbee_state(full_path)
                        if size == 0:
                            is_dir = True
                        items.append([item, size, is_dir])
                    return sorted(items, key=lambda x: (not x[2], x[0].lower()))
                except Exception as e:
                    return []
            print(json.dumps(get_detailed_listing('{dir}')))
        """
        
        try:
            out = self.repl.exec(command)
            return json.loads(out.decode("utf-8").strip())
        except (json.JSONDecodeError, ProtocolError):
            return []
    
    def _ls_detailed_standard(self, dir: str = "/") -> list:
        """
        Standard platform ls implementation (with stat() support).
        """
        if not dir.startswith("/"):
            dir = "/" + dir
        
        command = f"""
            import os
            import json
            def get_detailed_listing(path):
                try:
                    items = []
                    for item in os.listdir(path):
                        full_path = path + ('/' + item if path != '/' else item)
                        try:
                            stat_info = os.stat(full_path)
                            is_dir = stat_info[0] & 0x4000 != 0
                            size = 0 if is_dir else stat_info[6]
                            items.append([item, size, is_dir])
                        except:
                            try:
                                os.listdir(full_path)
                                items.append([item, 0, True])
                            except:
                                items.append([item, 0, False])
                    return sorted(items, key=lambda x: (not x[2], x[0].lower()))
                except:
                    return []
            print(json.dumps(get_detailed_listing('{dir}')))
        """
        
        try:
            out = self.repl.exec(command)
            return json.loads(out.decode("utf-8").strip())
        except (json.JSONDecodeError, ProtocolError):
            return []
    
    def _ls_recursive_xbee(self, dir: str = "/") -> list:
        """
        XBee-specific recursive ls implementation.
        """
        if not dir.startswith("/"):
            dir = "/" + dir
        
        command = f"""
            import os
            import json
            
            def xbee3_zigbee_state(path):
                try:
                    with open(path, 'rb') as f:
                        f.seek(0, 2)
                        size = f.tell()
                    return size
                except Exception as e:
                    return 0

            def get_recursive_listing(path, base_path=None):
                if base_path is None:
                    base_path = path
                items = []
                try:
                    for item in os.listdir(path):
                        full_path = path + ('/' + item if path != '/' else item)
                        
                        if base_path == '/':
                            rel_path = full_path
                        else:
                            rel_path = full_path[len(base_path):].lstrip('/')
                            if base_path != '/':
                                rel_path = base_path[1:] + '/' + rel_path if rel_path else base_path[1:]
                        
                        is_dir = False
                        size = xbee3_zigbee_state(full_path)
                        if size == 0:
                            is_dir = True
                        
                        if not is_dir:
                            items.append([rel_path, size, is_dir])
                        else:
                            items.extend(get_recursive_listing(full_path, base_path))
                    
                except Exception as e:
                    pass
                
                return sorted(items, key=lambda x: x[0].lower())

            print(json.dumps(get_recursive_listing('{dir}')))
        """
        
        try:
            out = self.repl.exec(command, soft_reset=False)
            return json.loads(out.decode("utf-8").strip())
        except (json.JSONDecodeError, ProtocolError):
            return self._ls_recursive_fallback(dir)
    
    def _ls_recursive_standard(self, dir: str = "/") -> list:
        """
        Standard platform recursive ls implementation.
        """
        if not dir.startswith("/"):
            dir = "/" + dir
        
        command = f"""
            import os
            import json

            def get_recursive_listing(path, base_path=None):
                if base_path is None:
                    base_path = path
                items = []
                try:
                    for item in os.listdir(path):
                        full_path = path + ('/' + item if path != '/' else item)
                        
                        if base_path == '/':
                            rel_path = full_path
                        else:
                            rel_path = full_path[len(base_path):].lstrip('/')
                            if base_path != '/':
                                rel_path = base_path[1:] + '/' + rel_path if rel_path else base_path[1:]
                        
                        try:
                            stat_info = os.stat(full_path)
                            is_dir = stat_info[0] & 0x4000 != 0
                            size = 0 if is_dir else stat_info[6]
                        except:
                            try:
                                os.listdir(full_path)
                                is_dir = True
                                size = 0
                            except:
                                is_dir = False
                                size = 0
                        
                        if not is_dir:
                            items.append([rel_path, size, is_dir])
                        else:
                            items.extend(get_recursive_listing(full_path, base_path))
                    
                except Exception as e:
                    pass
                
                return sorted(items, key=lambda x: x[0].lower())

            print(json.dumps(get_recursive_listing('{dir}')))
        """
        
        try:
            out = self.repl.exec(command)
            return json.loads(out.decode("utf-8").strip())
        except (json.JSONDecodeError, ProtocolError):
            return self._ls_recursive_fallback(dir)
    
    def _ls_recursive_fallback(self, dir: str = "/") -> list:
        """
        Fallback method for recursive directory listing.
        """
        result = []
        
        def walk_dir(current_dir, base_dir):
            items = self.ls_detailed(current_dir)
            for name, size, is_dir in items:
                full_path = posixpath.join(current_dir, name)
                # Get relative path
                if base_dir == '/':
                    rel_path = full_path
                else:
                    rel_path = full_path[len(base_dir):].lstrip('/')
                    if base_dir != '/':
                        rel_path = base_dir[1:] + '/' + rel_path if rel_path else base_dir[1:]
                
                if not is_dir:
                    result.append([rel_path, size, is_dir])
                else:
                    walk_dir(full_path, base_dir)
        
        try:
            walk_dir(dir, dir)
        except:
            pass
        
        return sorted(result, key=lambda x: x[0].lower())

    def mem(self) -> Tuple[int, int, int, float]:
        """
        Get the memory usage of the connected device.
        :return: A tuple containing (free_memory, alloc_memory, total_memory, usage_pct) in bytes.
        """
        command = f"""
            import gc
            gc.collect()
            free = gc.mem_free()
            alloc = gc.mem_alloc()
            total = free + alloc
            usage_pct = round(alloc / total * 100, 2)
            print(free, alloc, total, usage_pct)
        """
        out = self.repl.exec(command)
        free_str, alloc_str, total_str, usage_pct_str = out.decode("utf-8").strip().split()
        return int(free_str), int(alloc_str), int(total_str), float(usage_pct_str)
    
    def mkdir(self, dir: str) -> bool:
        """
        Create a directory on the connected device.
        :param dir: The directory to create.
        :return: True if the directory was created, False if it already exists.
        """
        command = f"""
            import os
            def mkdir(dir):
                parts = dir.split(os.sep)
                dirs = [os.sep.join(parts[:i+1]) for i in range(len(parts))]
                check = 0
                for d in dirs:
                    try:
                        os.mkdir(d)
                    except OSError as e:
                        check += 1
                        if "EEXIST" in str(e):
                            continue
                        else:
                            return False
                return check < len(parts)
            print(mkdir('{dir}'))
        """        
        out = self.repl.exec(command)
        return ast.literal_eval(out.decode("utf-8"))
    
    def getdir_batch(self, remote: str, local: str, progress_callback=None):
        """
        Download a directory and its contents from the device using optimized batch mode.
        
        :param remote: The remote directory path on the device.
        :param local: The local directory to save files.
        :param progress_callback: Optional callback(done, total, filename) for progress tracking
        :raises ProtocolError: If any file download fails
        """
        base_remote = remote.replace("\\", "/")
        base_local = os.path.abspath(local)
        
        # Get recursive listing of all files in the remote directory
        try:
            items = self.ls_recursive(base_remote)
        except Exception as e:
            raise ProtocolError(f"Failed to list remote directory: {e}")
        
        if not items:
            # Directory is empty or doesn't exist
            return
        
        # Create local directory structure and collect files to download
        file_specs = []
        for rel_path, size, is_dir in items:
            if is_dir:
                continue  # Skip directories (already handled by ls_recursive)
            
            # Calculate local path
            # rel_path is relative to base_remote
            local_path = os.path.join(base_local, rel_path.replace('/', os.sep))
            
            # Create parent directory if needed
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            # Full remote path
            if base_remote == '/':
                full_remote = '/' + rel_path
            else:
                full_remote = base_remote + ('/' if not base_remote.endswith('/') else '') + rel_path
            
            file_specs.append((full_remote, local_path))
        
        if not file_specs:
            return
        
        # Download all files
        total = len(file_specs)
        for idx, (remote_file, local_file) in enumerate(file_specs):
            if progress_callback:
                progress_callback(idx, total, os.path.basename(remote_file))
            
            try:
                self.get(remote_file, local_file)
            except Exception as e:
                raise ProtocolError(f"Failed to download {remote_file}: {e}")
        
        if progress_callback:
            progress_callback(total, total, "Complete")
    
    def putdir(self, local: str, remote: str):
        """
        Upload a directory and its contents to the connected device.
        :param local: The local directory to upload.
        :param remote: The remote directory path on the device.
        """
        base_local = os.path.abspath(local)
        base_remote = remote.replace("\\", "/")
        for parent, child_dirs, child_files in os.walk(base_local, followlinks=True):
            rel = os.path.relpath(parent, base_local).replace("\\", "/")
            remote_parent = posixpath.normpath(
                posixpath.join(base_remote, "" if rel == "." else rel)
            )
            try:
                self.mkdir(remote_parent)
            except Exception:
                pass

            for filename in child_files:
                local_path = os.path.join(parent, filename)
                remote_path = posixpath.join(remote_parent, filename).replace("\\", "/")
                self.put(local_path, remote_path)
    
    def put(self, local: str, remote: str, progress_callback=None):
        """
        Upload a file to the connected device.
        
        NOTE: WebREPL (Friendly REPL only) does not support file uploads due to
        lack of Raw REPL support. This method only works with Serial connections.
        
        :param local: The local file path to upload.
        :param remote: The remote file path on the device.
        :param progress_callback: Optional callback(bytes_sent, total_bytes) for progress tracking
        :raises ProtocolError: If the upload fails or if the file already exists.
        """
        if self.is_webrepl:
            raise ProtocolError("File upload (put) is not supported over WebREPL. Use Serial connection instead.")
        
        sent = 0
        needs_retry = False

        with self.repl.session():
            try:
                self.repl._exec(f"f = open('{remote}', 'wb')")
            except ProtocolError as e:
                if "EEXIST" in str(e):
                    needs_retry = True
                else:
                    raise
            else:
                with open(local, "rb") as f:
                    total = os.fstat(f.fileno()).st_size
                    
                    # Report initial progress
                    if progress_callback:
                        progress_callback(0, total)

                    batch_src_lines = []
                    batch_bytes = 0
                    DEVICE_CHUNK = self._DEVICE_CHUNK_SIZES
                    BATCH_LIMIT = max(8 * 1024, int(self._PUT_BATCH_BYTES))

                    def _flush_batch():
                        nonlocal batch_src_lines, batch_bytes, sent
                        if not batch_src_lines:
                            return

                        code = ";\n".join(batch_src_lines)
                        self.repl._exec(code)
                        batch_src_lines = []
                        batch_bytes = 0
                        
                        # Report progress after each batch flush
                        if progress_callback:
                            progress_callback(sent, total)

                    while True:
                        chunk = f.read(DEVICE_CHUNK)
                        if not chunk:
                            _flush_batch()
                            break

                        line = f"f.write({repr(chunk)})"
                        batch_src_lines.append(line)
                        batch_bytes += len(line)
                        sent += len(chunk)

                        if batch_bytes >= BATCH_LIMIT:
                            _flush_batch()

                self.repl._exec("f.close()")
                
                # Report completion
                if progress_callback:
                    progress_callback(total, total)

        if needs_retry:
            self.rm(remote)
            self.put(local, remote, progress_callback)
    
    def putdir_batch(self, local: str, remote: str, progress_callback=None):
        """
        Upload a directory and its contents using optimized batch mode.
        
        NOTE: WebREPL (Friendly REPL only) does not support file uploads due to
        lack of Raw REPL support. This method only works with Serial connections.
        
        This method reduces REPL overhead by uploading all files in a single session.
        
        :param local: The local directory to upload.
        :param remote: The remote directory path on the device.
        :param progress_callback: Optional callback(done, total, filename) for progress tracking
        :raises ProtocolError: If any file upload fails
        """
        if self.is_webrepl:
            raise ProtocolError("Directory upload (putdir_batch) is not supported over WebREPL. Use Serial connection instead.")
        
        base_local = os.path.abspath(local)
        base_remote = remote.replace("\\", "/")
        
        # Collect all files to upload
        file_specs = []
        for parent, child_dirs, child_files in os.walk(base_local, followlinks=True):
            rel = os.path.relpath(parent, base_local).replace("\\", "/")
            remote_parent = posixpath.normpath(
                posixpath.join(base_remote, "" if rel == "." else rel)
            )
            
            # Create remote directories (before batch upload starts)
            try:
                self.mkdir(remote_parent)
            except Exception:
                pass
            
            for filename in child_files:
                local_path = os.path.join(parent, filename)
                remote_path = posixpath.join(remote_parent, filename).replace("\\", "/")
                file_specs.append((local_path, remote_path))
        
        if not file_specs:
            return
        
        # Use batch mode for upload
        self.repl.put_files_batch(file_specs, progress_callback)
    
    def rm(self, filename: str):
        """
        Remove a file from the connected device.
        :param filename: The file to remove.
        """
        command = f"""
            import os
            os.remove('{filename}')
        """
        self.repl.exec(command)
    
    def rmdir(self, dir: str):
        """
        Remove a directory and all its contents recursively.
        :param dir: The directory to remove.
        """
        if self.core == "EFR32MG":
            command = f"""
                import os
                def rmdir(dir):
                    os.chdir(dir)
                    for f in os.listdir():
                        try:
                            os.remove(f)
                        except OSError:
                            pass
                    for f in os.listdir():
                        rmdir(f)
                    os.chdir('..')
                    os.rmdir(dir)
                rmdir('{dir}')
            """
        else:
            command = f"""
                import os
                def rmdir(p):
                    for name in os.listdir(p):
                        fp = p + '/' + name if p != '/' else '/' + name
                        try:
                            if os.stat(fp)[0] & 0x4000:
                                rmdir(fp)
                            else:
                                os.remove(fp)
                        except OSError:
                            try:
                                rmdir(fp)
                            except:
                                pass
                    os.rmdir(p)
                rmdir('{dir}')
            """
        self.repl.exec(command)
    
    def format(self) -> bool:
        """
        Format the filesystem of the connected device based on its core type.
        :return: True if the filesystem was successfully formatted, False otherwise.
        """
        if self.core in ("ESP32S3", "ESP32C6"): 
            command = """
                import os 
                from flashbdev import bdev 
                os.umount('/') 
                os.VfsLfs2.mkfs(bdev) 
                os.mount(bdev, '/') 
            """ 
        elif self.core == "EFR32MG": 
            command = """
                import os 
                os.format() 
            """
        elif self.core == "RP2350":
            command = """
                import os, rp2
                try:
                    os.umount('/')
                except:
                    pass
                bdev = rp2.Flash()
                os.VfsLfs2.mkfs(bdev, progsize=256)
                fs = os.VfsLfs2(bdev, progsize=256)
                os.mount(fs, '/')
            """ 
        else: 
            return False 
        
        try: 
            self.repl.exec(command) 
        except ProtocolError: 
            return False 
        return True
    
    def df(self):
        """
        Get filesystem information including total, used, free space and usage percentage.
        :return: A tuple containing total space, used space, free space, and usage percentage.
        """
        command = f"""
            import os
            import json
            def get_fs_info(path='/'):
                stats = os.statvfs(path)
                block_size = stats[0]
                total_blocks = stats[2]
                free_blocks = stats[3]

                total = block_size * total_blocks
                free = block_size * free_blocks
                used = total - free
                usage_pct = round(used / total * 100, 2)
                
                return total, used, free, usage_pct
            print(get_fs_info())
        """
        out = self.repl.exec(command)
        return ast.literal_eval(out.decode("utf-8"))
