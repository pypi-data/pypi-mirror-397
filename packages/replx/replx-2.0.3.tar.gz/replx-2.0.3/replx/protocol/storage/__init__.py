"""Storage operations for MicroPython devices."""

from .base import DeviceStorage
from .serial import SerialStorage
from .webrepl import WebREPLStorage


def create_storage(repl_protocol, core: str = "RP2350", device: str = "", device_root_fs: str = "/") -> DeviceStorage:
    """Factory function to create appropriate storage implementation."""
    if repl_protocol.transport.__class__.__name__ == "WebREPLTransport":
        return WebREPLStorage(
            repl_protocol,
            core=core,
            device=device,
            device_root_fs=device_root_fs
        )
    else:
        # Serial or other connection type
        return SerialStorage(
            repl_protocol,
            core=core,
            device=device,
            device_root_fs=device_root_fs
        )


__all__ = [
    'DeviceStorage',
    'SerialStorage',
    'WebREPLStorage',
    'create_storage',
]
