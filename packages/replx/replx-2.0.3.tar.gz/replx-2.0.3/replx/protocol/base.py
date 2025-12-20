"""MicroPython REPL Protocol implementation."""
import os
import sys
import time
import struct
import textwrap
import threading
from contextlib import contextmanager
from typing import Callable, Optional

import typer

try:
    import msvcrt
except ImportError:
    msvcrt = None

from ..exceptions import ProtocolError, TransportError
from ..transport import Transport, create_transport
from ..terminal import (
    IS_WINDOWS, CR, LF,
    flush_outbuf as _flush_outbuf,
    stdout_write_bytes as _stdout_write_bytes,
    getch, putch,
    utf8_need_follow as _utf8_need_follow,
    _EXTMAP,
)


class ReplProtocol:
    """MicroPython REPL protocol handler."""
    
    # Class-level SIGINT management
    _active_instance = None
    _sigint_handler_installed = False
    
    # Error filtering state (per-instance)
    _ERROR_HEADER = b"Traceback (most recent call last):"
    
    _REPL_BUFSIZE = 2048  # minimum 256
    
    # REPL Control Sequences (Official MicroPython Protocol)
    _CTRL_A = b'\x01'  # Enter raw REPL mode
    _CTRL_B = b'\x02'  # Exit raw REPL mode (friendly REPL)
    _CTRL_C = b'\x03'  # Interrupt/KeyboardInterrupt
    _CTRL_D = b'\x04'  # Soft reset / EOF marker
    _CTRL_E = b'\x05'  # Paste mode toggle / Raw-paste mode entry
    
    _EOF_MARKER = b'\x04'
    _RAW_REPL_PROMPT = b'raw REPL; CTRL-B to exit\r\n>'
    _SOFT_REBOOT_MSG = b'soft reboot\r\n'
    _OK_RESPONSE = b'OK'
    
    # Raw-Paste Mode Protocol (MicroPython v1.13+)
    _RAW_PASTE_INIT = b'\x05A\x01'  # Ctrl-E + 'A' + Ctrl-A to enter raw-paste
    _RAW_PASTE_SUPPORTED = b'R\x01'  # Device supports raw-paste mode
    _RAW_PASTE_NOT_SUPPORTED = b'R\x00'  # Device doesn't support raw-paste
    _RAW_PASTE_FALLBACK = b'raw REPL; CTRL-B'  # Legacy response (no raw-paste)
    _RAW_PASTE_WINDOW_INC = b'\x01'  # Flow control: increase window size
    _RAW_PASTE_END_DATA = b'\x04'  # Flow control: device wants to end reception
    
    def __init__(self, port:str, baudrate:int=115200, core:str="RP2350", device_root_fs:str="/", password:str=""):
        """
        Initialize the REPL protocol handler.
        :param port: The serial port or WebREPL URL (ws://host:port) to connect to.
        :param baudrate: The baud rate for the serial connection (default is 115200).
        :param core: The core type of the device (e.g., "RP2350", "ESP32", "EFR32MG").
        :param device_root_fs: The root filesystem path on the device.
        :param password: WebREPL password (for WebSocket connections).
        :raises ProtocolError: If the connection cannot be established or if the device is not found.
        """
        try:
            self.transport = create_transport(port, baudrate=baudrate, password=password)
            self._stop_event = threading.Event()
            self._follow_thread = None
        except Exception as e:
            raise ProtocolError(f"failed to open {port} ({e})")
        
        self._rx_pushback = bytearray()
        self._raw_paste_supported = None  # None=unknown, True=supported, False=not supported
        self._raw_paste_window_size = 128  # Default window size increment
        
        # Error filtering state (instance-level)
        self._skip_error_output = False
        self._error_header_buf = b""
        
        # Device-specific attributes
        self.core = core
        self.device_root_fs = device_root_fs
        self._DEVICE_CHUNK_SIZES = 4096
        self._PUT_BATCH_BYTES = 16 * 1024
        
        self._init_repl()
        self._install_sigint_handler()

    @classmethod
    def _install_sigint_handler(cls):
        """Install Windows SIGINT handler (once per process)."""
        if IS_WINDOWS and not cls._sigint_handler_installed:
            import signal
            
            def win_sigint_handler(signum, frame):
                """Handle SIGINT on Windows - send interrupt to active REPL."""
                if cls._active_instance is not None:
                    try:
                        cls._active_instance.request_interrupt()
                    except Exception:
                        pass
            
            try:
                signal.signal(signal.SIGINT, win_sigint_handler)
                cls._sigint_handler_installed = True
            except Exception:
                pass
    
    def _reset_error_filter(self):
        """Reset error output filtering state."""
        self._skip_error_output = False
        self._error_header_buf = b""

    def _init_repl(self):
        """
        Initialize the REPL (Read-Eval-Print Loop) for the Replx.
        This function sets up the serial connection and prepares the board for REPL interaction.
        """
        self._interrupt_requested = False
        self._session_depth = 0
        self._in_raw_repl = False  # Track if currently in RAW REPL mode
        self._repl_prompt_detected = False  # Track if >>> prompt was received

    def _read(self, n:int=1) -> bytes:
        """
        Read a specified number of bytes from the serial port.
        :param n: Number of bytes to read from the serial port.
        :return: The bytes read from the serial port.
        """
        if self._rx_pushback:
            if len(self._rx_pushback) <= n:
                b = bytes(self._rx_pushback)
                self._rx_pushback.clear()
                rem = n - len(b)
                if rem > 0:
                    b += self.transport.read(rem)
            else:
                b = bytes(self._rx_pushback[:n])
                del self._rx_pushback[:n]
        else:
            b = self.transport.read(n)

        return b
    
    def _read_ex(self, min_num_bytes:int, ending:bytes, timeout:int=5,
                data_consumer:Optional[Callable[[bytes], None]]=None) -> bytes:
        """
        Read data until ending pattern is found.
        
        For streaming mode (timeout=0 with data_consumer), uses memory-efficient
        approach that discards consumed data immediately.
        This allows infinite runtime without memory growth.
        """
        start = time.time()
        deadline = (start + timeout) if timeout > 0 else None
        
        # Streaming mode: don't accumulate data, only track for pattern matching
        # This is critical for long-running operations (365 days+)
        streaming_mode = (timeout == 0 and data_consumer is not None)
        
        # KMP pattern matching setup
        pat = ending
        m = len(pat)
        pi = [0] * m
        k = 0
        for i in range(1, m):
            while k > 0 and pat[k] != pat[i]:
                k = pi[k-1]
            if pat[k] == pat[i]:
                k += 1
            pi[i] = k

        matched = 0
        
        # For streaming mode: only keep last few bytes for return value
        # For non-streaming: accumulate all data
        tail_size = m + 8
        tail_buffer = bytearray(tail_size)
        tail_len = 0  # Actual bytes in tail_buffer (up to tail_size)
        data = bytearray()  # Used only in non-streaming mode
        
        def _call_consumer(chunk: bytes):
            """Call data_consumer directly with each chunk."""
            if data_consumer and chunk:
                try:
                    data_consumer(chunk)
                except Exception:
                    pass

        def _update_tail(chunk: bytes):
            """Update tail buffer with new chunk (circular buffer style)."""
            nonlocal tail_len
            chunk_len = len(chunk)
            if chunk_len >= tail_size:
                # Chunk is larger than buffer, just keep last tail_size bytes
                tail_buffer[:] = chunk[-tail_size:]
                tail_len = tail_size
            elif tail_len + chunk_len <= tail_size:
                # Fits in remaining space
                tail_buffer[tail_len:tail_len + chunk_len] = chunk
                tail_len += chunk_len
            else:
                # Need to shift: keep last (tail_size - chunk_len) bytes, append chunk
                keep = tail_size - chunk_len
                tail_buffer[:keep] = tail_buffer[tail_len - keep:tail_len]
                tail_buffer[keep:keep + chunk_len] = chunk
                tail_len = tail_size

        def _feed_chunk(chunk: bytes) -> int:
            nonlocal matched

            if not chunk:
                return -1

            end_at = -1
            for idx, b in enumerate(chunk):
                while matched > 0 and pat[matched] != b:
                    matched = pi[matched - 1]
                if pat[matched] == b:
                    matched += 1
                    if matched == m:
                        end_at = idx
                        break

            if streaming_mode:
                # Streaming: only keep tail, don't accumulate
                chunk_to_process = chunk[:end_at+1] if end_at >= 0 else chunk
                _call_consumer(chunk_to_process)
                _update_tail(chunk_to_process)
                return end_at + 1 if end_at >= 0 else -1
            else:
                # Non-streaming: accumulate all data
                if end_at >= 0:
                    data.extend(chunk[:end_at+1])
                    _call_consumer(chunk[:end_at+1])
                    return end_at + 1
                
                data.extend(chunk)
                _call_consumer(chunk)
                return -1

        def _read_some(max_n: int) -> bytes:
            """Read available bytes, using non-blocking read_available when possible."""
            # First check pushback buffer
            if self._rx_pushback:
                return self._read(max(1, max_n))
            # Use non-blocking read_available for better responsiveness
            try:
                avail = self.transport.read_available()
                if avail:
                    return avail  # Return all available data, KMP handles it
            except Exception:
                pass
            # In streaming mode, don't block - return empty to allow polling loop to continue
            # This is critical for scripts with time.sleep() where output is delayed
            if streaming_mode:
                return b''
            # Fallback to blocking read with small amount (non-streaming mode only)
            return self._read(1)

        def _get_result() -> bytes:
            """Get the result data."""
            if streaming_mode:
                # Return only the tail buffer content
                return bytes(tail_buffer[:tail_len])
            else:
                return bytes(data)

        try:
            if min_num_bytes > 0:
                chunk = _read_some(min_num_bytes)
                if chunk:  # Only process if we got data (streaming mode may return empty)
                    pos = _feed_chunk(chunk)
                    if pos >= 0:
                        tail = chunk[pos:]
                        if tail:
                            self._rx_pushback[:] = tail + self._rx_pushback
                        return _get_result()

            last_activity = time.time()
            last_keepalive = time.time()
            keepalive_interval = 30.0  # Send keep-alive every 30 seconds

            while True:
                if self._stop_event.is_set():
                    break
                
                if deadline is not None and time.time() >= deadline:
                    break
                
                # Periodic keep-alive for long-running streaming operations
                now = time.time()
                if streaming_mode and (now - last_keepalive) >= keepalive_interval:
                    try:
                        if hasattr(self.transport, 'keep_alive'):
                            self.transport.keep_alive()
                        last_keepalive = now
                    except Exception:
                        pass

                # Check pushback buffer first
                waiting = self.transport.in_waiting()
                if waiting <= 0 and len(self._rx_pushback) > 0:
                    waiting = 1

                if waiting > 0:
                    # Read available bytes - KMP handles partial matches correctly
                    # Read larger chunks for better throughput
                    want = min(4096, max(256, waiting))
                    chunk = _read_some(want)
                    if chunk:
                        pos = _feed_chunk(chunk)
                        last_activity = time.time()
                        if pos >= 0:
                            tail = chunk[pos:]
                            if tail:
                                self._rx_pushback[:] = tail + self._rx_pushback
                            return _get_result()
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.001)
                    # Idle timeout handling:
                    # - With timeout > 0: use timeout * 2 or minimum 10 seconds
                    # - With data_consumer (streaming for run): 3600 seconds (1 hour) to allow input() waits
                    # - Without data_consumer: 5 seconds to prevent infinite hang
                    if timeout > 0:
                        idle_limit = max(timeout * 2, 10)
                    elif data_consumer is not None:
                        # Streaming mode with consumer: long timeout for interactive input()
                        idle_limit = 3600  # 1 hour - user may take time to respond to input()
                    else:
                        idle_limit = 5  # 5 seconds idle timeout for non-interactive streaming
                    if (time.time() - last_activity) > idle_limit:
                        break

            return _get_result()

        except TransportError as e:
            if not self._stop_event.is_set():
                raise ProtocolError(f"Transport communication error: {e}")
            return _get_result()
        except ProtocolError:
            raise
        except Exception:
            return _get_result()


    def _enter_repl(self):
        """
        Enter the raw REPL mode of the device.
        This function sends the necessary commands to the device to enter the raw REPL mode.
        No soft reset is performed - use _soft_reset() explicitly if needed.
        """
        for attempt in (1, 2):
            try:
                self.transport.reset_input_buffer()
            except Exception:
                pass

            self.transport.write(b'\r' + self._CTRL_C + self._CTRL_C)
            time.sleep(0.05)
            try:
                self.transport.reset_input_buffer()
            except Exception:
                pass
            
            self.transport.write(b'\r' + self._CTRL_A)

            try:
                data = self._read_ex(1, self._RAW_REPL_PROMPT[:-1], timeout=3)
                if not data.endswith(self._RAW_REPL_PROMPT[:-1]):
                    raise ProtocolError('could not enter raw repl')
                self._in_raw_repl = True
                return
            except ProtocolError:
                try:
                    self.transport.write(b'\r' + self._CTRL_B)  # friendly
                    time.sleep(0.1)
                except Exception:
                    pass
                time.sleep(0.12)
                continue
            
        raise ProtocolError('could not enter raw repl')

    def _soft_reset(self):
        """
        Perform a soft reset of the device while in raw REPL mode.
        Should be called only when a clean slate is needed (e.g., run command).
        """
        try:
            # Send Ctrl+C first to interrupt any running code (e.g., infinite loops)
            self.transport.write(self._CTRL_C)
            time.sleep(0.1)
            self.transport.write(self._CTRL_C)
            time.sleep(0.1)
            self.transport.reset_input_buffer()
            
            # Re-enter raw REPL mode after interrupt
            self.transport.write(self._CTRL_A)
            time.sleep(0.1)
            self.transport.reset_input_buffer()
            
            # Send Ctrl+D to trigger soft reset
            self.transport.write(self._CTRL_D)
            data = self._read_ex(1, self._SOFT_REBOOT_MSG, timeout=3)
            if not data.endswith(self._SOFT_REBOOT_MSG):
                raise ProtocolError('soft reset failed')
            
            # Wait for raw REPL prompt after reset
            data = self._read_ex(1, self._RAW_REPL_PROMPT[:-1], timeout=3)
            if not data.endswith(self._RAW_REPL_PROMPT[:-1]):
                raise ProtocolError('soft reset failed')
        except Exception as e:
            raise

    def _resync_repl(self):
        """Attempt a fast raw-REPL resynchronization without full leave/enter."""
        try:
            self.transport.write(b'\r' + self._CTRL_B)
            time.sleep(0.04)
            self.transport.reset_input_buffer()
        except Exception:
            pass

        try:
            self.transport.write(b'\r' + self._CTRL_A)
            got = self._read_ex(1, self._RAW_REPL_PROMPT[:-1], timeout=1)
            if got.endswith(self._RAW_REPL_PROMPT[:-1]):
                return True
        except Exception:
            pass
        return False

    def _leave_repl(self):
        """
        Leave the raw REPL mode of the device.
        """
        self.transport.write(b'\r' + self._CTRL_B)  # enter friendly REPL
        self._in_raw_repl = False

    @contextmanager
    def session(self):
        """Context manager to reuse a single raw REPL session across operations."""
        need_enter = self._session_depth == 0
        if need_enter:
            self._enter_repl()
        self._session_depth += 1
        try:
            yield
        finally:
            self._session_depth = max(0, self._session_depth - 1)
            if need_enter:
                self._leave_repl()

    def _enter_raw_paste_mode(self) -> bool:
        """
        Attempt to enter raw-paste mode within raw REPL.
        Returns True if raw-paste mode is supported and entered successfully, False otherwise.
        
        Protocol (from MicroPython official docs):
        1. Already in raw REPL mode (via Ctrl-A)
        2. Send b'\x05A\x01' (Ctrl-E + 'A' + Ctrl-A)
        3. Read 2 bytes response:
           - b'R\x01' = raw-paste supported, entered successfully
           - b'R\x00' = device understands but doesn't support
           - b'ra' = old device, doesn't understand (read rest of prompt and discard)
        4. If b'R\x01', read 2 more bytes as little-endian window size increment
        """
        if self._raw_paste_supported is not None:
            return self._raw_paste_supported
        
        try:
            # Step 2: Send raw-paste initialization sequence
            self.transport.write(self._RAW_PASTE_INIT)
            
            # Step 3: Read 2-byte response
            response = self._read(2)
            
            if response == self._RAW_PASTE_SUPPORTED:
                # Step 4: Read window size increment (2 bytes, little-endian uint16)
                window_bytes = self._read(2)
                if len(window_bytes) == 2:
                    self._raw_paste_window_size = struct.unpack('<H', window_bytes)[0]
                    self._raw_paste_supported = True
                    return True
                else:
                    self._raw_paste_supported = False
                    return False
                    
            elif response == self._RAW_PASTE_NOT_SUPPORTED:
                self._raw_paste_supported = False
                return False
                
            elif response.startswith(b'r'):
                # Legacy device - read and discard rest of prompt
                # Try to read the rest: 'aw REPL; CTRL-B to exit\r\n>'
                try:
                    rest = self._read_ex(1, b'>', timeout=1)
                except Exception:
                    pass
                self._raw_paste_supported = False
                return False
                
            else:
                self._raw_paste_supported = False
                return False
                
        except Exception as e:
            self._raw_paste_supported = False
            return False

    def _follow_task(self, echo: bool):
        try:
            while not self._stop_event.is_set():
                try:
                    if IS_WINDOWS:
                        # Use terminal.getch() for cross-platform compatibility
                        import msvcrt
                        if msvcrt.kbhit():
                            w = msvcrt.getwch()
                            if w in ("\x03",):  # Ctrl+C
                                self.request_interrupt()
                                time.sleep(0.1)
                                return
                            if w in ("\x04",):   # Ctrl+D
                                try: 
                                    self.transport.write(self._CTRL_D)
                                except: 
                                    pass
                                time.sleep(0.08)
                                return
                            
                            # Handle extended keys (arrows, Del, etc.) in Windows
                            if w in ("\x00", "\xe0"):  # Extended key prefix
                                ext_key = msvcrt.getwch()
                                ch = _EXTMAP.get(ext_key, b"")
                                if not ch:  # Unknown extended key, skip
                                    time.sleep(0.005)
                                    continue
                                # Echo ON: Display ANSI escape sequence on PC
                                if echo:
                                    putch(ch)
                            else:
                                ch = w.encode("utf-8")
                                # Echo ON: Display typed character on PC
                                if echo:
                                    putch(ch)
                        else:
                            time.sleep(0.005)
                            continue
                    else:
                        # POSIX
                        import select
                        r, _, _ = select.select([sys.stdin], [], [], 0.005)
                        if not r:
                            continue
                        first = os.read(sys.stdin.fileno(), 1)
                        need = _utf8_need_follow(first[0])
                        ch = first + (os.read(sys.stdin.fileno(), need) if need else b"")
                        # Echo ON: Display typed character on PC
                        if echo:
                            putch(ch)

                    self.transport.write(CR if ch == LF else ch)
                except Exception:
                    pass
        finally:
            pass

    def _exec_raw_paste(self, command: bytes, data_consumer: Optional[Callable[[bytes], None]] = None) -> tuple[bytes, bytes]:
        """
        Execute command using raw-paste mode with flow control.
        Returns (stdout_data, stderr_data).
        
        Protocol steps (from MicroPython official docs):
        1. Already in raw REPL and raw-paste mode
        2. Read initial window size (already done in _enter_raw_paste_mode)
        3. Send code with flow control:
           - Track remaining window size
           - When window exhausted, wait for b'\x01' (window increment) or b'\x04' (end)
        4. Send b'\x04' when all code sent
        5. Read b'\x04' acknowledgment
        6. Read execution output until b'\x04'
        7. Read error output until b'\x04'
        8. Read final b'>' prompt
        """
        # Step 3-4: Send code with flow control
        remaining_window = self._raw_paste_window_size * 2  # Initial window (2x increment)
        bytes_sent = 0
        command_len = len(command)
        
        while bytes_sent < command_len:
            # Wait for window space
            while remaining_window <= 0:
                fc_byte = self._read(1)
                if fc_byte == self._RAW_PASTE_WINDOW_INC:
                    remaining_window += self._raw_paste_window_size
                elif fc_byte == self._RAW_PASTE_END_DATA:
                    self.transport.write(self._CTRL_D)
                    break
                else:
                    raise ProtocolError("Raw-paste flow control error")
            
            if fc_byte == self._RAW_PASTE_END_DATA:
                break
            
            # Send chunk
            chunk_size = min(remaining_window, command_len - bytes_sent)
            chunk = command[bytes_sent:bytes_sent + chunk_size]
            self.transport.write(chunk)
            bytes_sent += chunk_size
            remaining_window -= chunk_size
            
            # Check for flow control without blocking
            if self.transport.in_waiting() > 0:
                fc_byte = self._read(1)
                if fc_byte == self._RAW_PASTE_WINDOW_INC:
                    remaining_window += self._raw_paste_window_size
                elif fc_byte == self._RAW_PASTE_END_DATA:
                    self.transport.write(self._CTRL_D)
                    break
        
        # Step 4: Signal end of data
        if bytes_sent == command_len:
            self.transport.write(self._CTRL_D)
        
        # Step 5: Read compilation acknowledgment (b'\x04')
        ack = self._read_ex(1, self._EOF_MARKER, timeout=5)
        if not ack.endswith(self._EOF_MARKER):
            raise ProtocolError("Raw-paste compilation acknowledgment timeout")
        
        # Step 6: Read stdout until b'\x04'
        stdout_data = self._read_ex(1, self._EOF_MARKER, timeout=0, data_consumer=data_consumer)
        if stdout_data.endswith(self._EOF_MARKER):
            stdout_data = stdout_data[:-1]
        
        # Step 7: Read stderr until b'\x04'
        stderr_data = self._read_ex(1, self._EOF_MARKER, timeout=5)
        if stderr_data.endswith(self._EOF_MARKER):
            stderr_data = stderr_data[:-1]
        
        # Step 8: Read final prompt '>'
        prompt = self._read(1)
        
        return (stdout_data, stderr_data)

    def _exec(self, command:str|bytes, interactive:bool=False, echo:bool=False, detach:bool=False, 
              data_consumer:Optional[Callable[[bytes], None]]=None) -> bytes:
        """
        Execute a command on the device and return the output.
        Automatically uses raw-paste mode if supported for better performance and reliability.
        Falls back to standard raw mode if raw-paste is not available.
        :param command: The command to execute.
        :param interactive: If True, stream the output to stdout and handle keyboard input.
        :param echo: If True, echo the command to stdout.
        :param detach: If True, return immediately without waiting for output.
        :param data_consumer: Optional callback for streaming output. If provided, output is streamed via this callback.
        :return: The output of the command as bytes.
        """
        self._stop_event.clear()
        self._reset_error_filter()
        
        if isinstance(command, str):
            command = command.encode('utf-8')
        
        data_err = b''
        # Use provided data_consumer, or create default one for interactive mode
        if data_consumer is None and interactive:
            data_consumer = self._create_data_consumer()
        follow_thread = None   

        if interactive:
            # Set this instance as active for SIGINT handling
            ReplProtocol._active_instance = self

        # Read initial '>' prompt from raw REPL
        data = self._read_ex(1, b'>')
        if not data.endswith(b'>'):
            raise ProtocolError('could not enter raw repl')

        command_len = len(command)

        # Raw-paste mode disabled - has issues with streaming output
        use_raw_paste = False
        
        if use_raw_paste:
            try:
                data, data_err = self._exec_raw_paste(command, data_consumer)
                
                if data_err:
                    if self._interrupt_requested:
                        data_err = b""
                    else:
                        raise ProtocolError(data_err.decode('utf-8', errors='replace'))
                
                self._interrupt_requested = False
                return data
            except Exception as e:
                # Mark as not supported and fall through to standard mode
                self._raw_paste_supported = False
                # Attempt lightweight resync before expensive leave/enter cycle
                if not self._resync_repl():
                    self._leave_repl()
                    time.sleep(0.05)
                    self._enter_repl()
                    data = self._read_ex(1, b'>')
                    if not data.endswith(b'>'):
                        raise ProtocolError('could not recover after raw-paste failure')
        
        # Standard raw mode execution (original implementation)
        current_buffer_size = 4096  # Fixed optimal size for RP2350
        bytes_sent = 0
        
        start_time = time.time()
        
        while bytes_sent < command_len:
            chunk_end = min(bytes_sent + current_buffer_size, command_len)
            chunk = command[bytes_sent:chunk_end]
            
            self.transport.write(chunk)
            bytes_sent += len(chunk)
        
        self.transport.write(self._EOF_MARKER)
        
        transfer_time = time.time() - start_time
        timeout = max(5, int(transfer_time * 2))
        
        data = self._read_ex(1, self._OK_RESPONSE, timeout=timeout)
        if not data.endswith(self._OK_RESPONSE):
            raise ProtocolError('could not execute command (response: %r)' % data)

        if detach:
            return b''
        
        if interactive:
            self._stop_event.clear()
            self._interrupt_requested = False
            follow_thread = threading.Thread(target=self._follow_task, args=(echo,), daemon=True)
            follow_thread.start()
            
        try:
            # Read stdout
            data = self._read_ex(1, self._EOF_MARKER, 0, data_consumer)
            if data.endswith(self._EOF_MARKER):
                data = data[:-1]
            
            # Read stderr
            data_err = self._read_ex(1, self._EOF_MARKER, 0, None)
            if data_err.endswith(self._EOF_MARKER):
                data_err = data_err[:-1]
            elif data_err and not self._interrupt_requested:
                raise ProtocolError(data_err.decode('utf-8', errors='replace'))
        finally:            
            def _drain_consumer(b: bytes, _carry=[False]):
                if len(b) == 1 and b == b'>':
                    return
                _stdout_write_bytes(b)
    
            if follow_thread and follow_thread.is_alive():
                self._stop_event.set()
                try: 
                    follow_thread.join(timeout=0.05)
                except Exception:
                    pass
                
                self._stop_event.clear()
                
                try:
                    self._read_ex(1, self._EOF_MARKER, timeout=0.1, data_consumer=_drain_consumer)
                except Exception:
                    pass

                try:
                    _flush_outbuf()
                except Exception:
                    pass

                try:
                    if self._interrupt_requested and self.core != "EFR32MG":
                        self.transport.write(b'\r' + self._CTRL_B)
                        time.sleep(0.08)
                        self.transport.write(b'\r' + self._CTRL_A)
                        self._read_ex(1, self._RAW_REPL_PROMPT[:-1], timeout=1)
                    else:
                        self.transport.write(self._CTRL_D)
                        got = self._read_ex(1, self._SOFT_REBOOT_MSG, timeout=2)
                        if not got.endswith(self._SOFT_REBOOT_MSG):
                            self.transport.write(b'\r' + self._CTRL_B)
                            time.sleep(0.08)
                            self.transport.write(b'\r' + self._CTRL_A)
                            self._read_ex(1, self._RAW_REPL_PROMPT[:-1], timeout=1)
                except Exception:
                    pass
        
        # Clean up active instance
        if interactive:
            ReplProtocol._active_instance = None
        
        if data_err:
            if self._interrupt_requested:
                data_err = b""
            else:
                raise ProtocolError(data_err.decode('utf-8', errors='replace'))

        self._interrupt_requested = False
        return data
    
    def _create_data_consumer(self):
        """Create data consumer with error filtering and immediate flush for real-time output."""
        def data_consumer(chunk):
            if not chunk:
                return
            
            # Error filtering logic
            self._error_header_buf = (self._error_header_buf + chunk)[-len(self._ERROR_HEADER):]
            if self._error_header_buf == self._ERROR_HEADER:
                self._skip_error_output = True
                return
            
            if not self._skip_error_output:
                _stdout_write_bytes(chunk)
                # Flush immediately for real-time output in interactive mode
                _flush_outbuf()
        
        return data_consumer

    def _drain_eof(self, max_ms:int=200):
        """
        Drain the serial input buffer until EOF is received or timeout occurs.
        :param max_ms: Maximum time to wait for EOF in milliseconds.
        """
        deadline = time.time() + max_ms / 1000
        while time.time() < deadline:
            waiting = self.transport.in_waiting()
            if waiting:
                _ = self._read(waiting) 
            else:
                time.sleep(0.01)

    def _repl_serial_to_stdout(self):
        """
        Read data from the serial port and write it to stdout.
        """
        # ANSI color codes for REPL prompts
        PROMPT_COLOR = b"\033[92m"  # Bright green for >>>
        CONT_COLOR = b"\033[93m"    # Bright yellow for ...
        RESET_COLOR = b"\033[0m"
        
        try:
            while self.serial_reader_running:
                try:
                    count = self.transport.in_waiting()
                except Exception:
                    break

                if not count:
                    time.sleep(0.01)
                    continue

                try:
                    data = self.transport.read(count)
                except Exception:
                    break

                if not data:
                    continue

                # Detect prompt for synchronization
                if b">>> " in data:
                    self._repl_prompt_detected = True

                if self.serial_out_put_enable and self.serial_out_put_count > 0:
                    # Colorize REPL prompts
                    data = data.replace(b">>> ", PROMPT_COLOR + b">>> " + RESET_COLOR)
                    data = data.replace(b"... ", CONT_COLOR + b"... " + RESET_COLOR)
                    
                    if IS_WINDOWS:
                        sys.stdout.buffer.write(data.replace(b"\r", b""))
                    else:
                        sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()

                self.serial_out_put_count += 1
        except KeyboardInterrupt:
            try:
                self.transport.close()
            except Exception:
                pass

    def _reset(self):
        """
        Reset the device by executing a soft reset command. 
        """
        command = f"""
            import machine
            machine.soft_reset()  # Ctrl+D
        """
        self.exec(command)

    def request_interrupt(self):
        self._interrupt_requested = True
        try:
            self.transport.write(self._CTRL_C)
        except Exception:
            pass

    def exec(self, command:str=None):
        """
        Run a command or script on the device.
        :param command: The command to execute.
        """
        # Skip _enter_repl if already in RAW REPL
        if not self._in_raw_repl:
            self._enter_repl()
        
        try:
            command = textwrap.dedent(command)
            return self._exec(command)
        finally:
            # Stay in RAW REPL for next call (stateful connection)
            pass
    
    def run(self, local, interactive:bool=False, echo:bool=False):
        """
        Run a command or script on the device with isolated execution environment.
        Stays in RAW REPL mode after execution for stateful connection.
        :param local: Path to the script file to execute.
        :param interactive: If True, stream the output to stdout.
        :param echo: If True, echo the command to stdout.
        """
        if not interactive and echo:
            raise typer.BadParameter("Option chaining error: -n and -e can only be used once, not multiple times.")
        
        # Enter REPL if not already in it
        if not self._in_raw_repl:
            self._enter_repl()
        
        try:
            self._soft_reset()
            with open(local, "rb") as f:
                data = f.read()
            # non-interactive mode: detach immediately after sending script
            # interactive mode: wait for completion and handle I/O
            self._exec(data, interactive, echo, detach=not interactive)
            if interactive:
                self._drain_eof(max_ms=200)
        except Exception as e:
            # On error, leave REPL and re-raise
            self._leave_repl()
            raise
    
    def put_files_batch(self, file_specs: list[tuple[str, str]], progress_callback: Optional[Callable[[int, int, str], None]] = None):
        """
        Upload multiple files in a single REPL session (optimized batch mode).
        This method minimizes REPL enter/exit overhead by batching multiple file uploads.
        
        :param file_specs: List of (local_path, remote_path) tuples to upload
        :param progress_callback: Optional callback(done, total, filename) for progress tracking
        :raises ProtocolError: If any file upload fails
        """
        if not file_specs:
            return
        
        total = len(file_specs)
        
        # Single REPL enter/exit for entire batch
        with self.session():
            for idx, (local_path, remote_path) in enumerate(file_specs):
                if progress_callback:
                    try:
                        progress_callback(idx, total, os.path.basename(remote_path))
                    except Exception:
                        pass
                
                # Open file on device
                self._exec(f"f = open('{remote_path}', 'wb')")
                
                try:
                    with open(local_path, 'rb') as f_local:
                        file_size = os.fstat(f_local.fileno()).st_size
                        DEVICE_CHUNK = self._DEVICE_CHUNK_SIZES
                        
                        batch_lines = []
                        batch_bytes = 0
                        BATCH_LIMIT = max(8 * 1024, int(self._PUT_BATCH_BYTES))
                        
                        while True:
                            chunk = f_local.read(DEVICE_CHUNK)
                            if not chunk:
                                # Flush final batch
                                if batch_lines:
                                    code = ";\n".join(batch_lines)
                                    self._exec(code)
                                break
                            
                            line = f"f.write({repr(chunk)})"
                            batch_lines.append(line)
                            batch_bytes += len(line)
                            
                            if batch_bytes >= BATCH_LIMIT:
                                code = ";\n".join(batch_lines)
                                self._exec(code)
                                batch_lines = []
                                batch_bytes = 0
                    
                    # Close file on device
                    self._exec("f.close()")
                    
                except Exception as e:
                    # Attempt to close file on device before re-raising
                    try:
                        self._exec("f.close()")
                    except Exception:
                        pass
                    raise ProtocolError(f"Failed to upload {local_path}: {e}")
            
            if progress_callback:
                try:
                    progress_callback(total, total, "")
                except Exception:
                    pass
    
    def close(self):
        """
        Close the transport connection.
        """
        self.transport.close()

    def reset(self):
        """
        Reset the device by performing a soft reset.
        Stays in RAW REPL mode after reset for stateful connection.
        """
        if not self._in_raw_repl:
            self._enter_repl()
        
        try:
            self._soft_reset()
        except Exception as e:
            # On error, leave REPL and re-raise
            self._leave_repl()
            raise
 
    def repl(self):
        """
        Enter the REPL mode, allowing interaction with the device.
        Type 'exit' and press Enter to exit REPL mode.
        """
        import time
        
        # Initialize REPL-specific variables
        self.serial_reader_running = True
        self.serial_out_put_enable = False  # Suppress output until we get clean prompt
        self.serial_out_put_count = 0
        self._repl_prompt_detected = False

        # Start reader thread FIRST so it can capture all output
        repl_thread = threading.Thread(target=self._repl_serial_to_stdout, daemon=True, name='REPL')
        repl_thread.start()
        
        # Small delay to ensure reader thread is running
        time.sleep(0.05)

        # Send Ctrl+B to exit RAW REPL mode (if in it), then Ctrl+C to interrupt
        self.transport.write(self._CTRL_B)  # Exit raw REPL -> friendly REPL
        time.sleep(0.05)
        self.transport.write(self._CTRL_C)  # Interrupt any running code
        time.sleep(0.1)
        
        # Drain all pending output (banner, old prompts, etc.)
        drain_timeout = time.time() + 0.5
        while time.time() < drain_timeout:
            if self.transport.in_waiting() > 0:
                self.transport.read(self.transport.in_waiting())
                time.sleep(0.02)
            else:
                time.sleep(0.05)
                # If no more data for a moment, we're done draining
                if self.transport.in_waiting() == 0:
                    break
        
        # Now enable output and request a single clean prompt
        self.serial_out_put_enable = True
        self.serial_out_put_count = 1
        self.transport.write(b'\r')  # Request fresh prompt
        
        # Wait for prompt (>>> should appear)
        prompt_timeout = time.time() + 1.0
        while time.time() < prompt_timeout:
            time.sleep(0.05)
            if self._repl_prompt_detected:
                break
        
        # Ring buffer for 'exit' detection (only track last 6 chars: "exit()")
        # This avoids growing buffer for long input lines
        recent_chars = bytearray(6)
        recent_len = 0
        
        while True:
            char = getch()

            if char == b'\x07': 
                self.serial_out_put_enable = False
                continue
            elif char == b'\x0F': 
                self.serial_out_put_enable = True
                self.serial_out_put_count = 0
                continue
            elif char == b'\x00' or not char: # Ignore null characters
                continue
            
            # Check for 'exit' on Enter
            if char == b'\r' or char == b'\n':
                # Check recent input for 'exit' or 'exit()'
                if recent_len >= 4:
                    cmd = bytes(recent_chars[:recent_len]).strip().lower()
                    if cmd in (b'exit', b'exit()'):
                        break
                recent_len = 0
            elif char == b'\x7f' or char == b'\x08':  # Backspace
                if recent_len > 0:
                    recent_len -= 1
            elif char >= b' ' and len(char) == 1:  # Printable character
                if recent_len < 6:
                    recent_chars[recent_len] = char[0]
                    recent_len += 1
                else:
                    # Shift left and add new char (only keep last 6)
                    recent_chars[:-1] = recent_chars[1:]
                    recent_chars[5] = char[0]
            
            try:
                self.transport.write(b'\r' if char == b'\n' else char)
            except:
                break
            
        self.serial_reader_running = False
        print('')

