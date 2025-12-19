"""OS detection and dependency checking utilities"""

import platform
import subprocess
import sys
import os


# Platform constants
PLATFORM_WINDOWS = "windows"
PLATFORM_LINUX = "linux"
PLATFORM_MACOS = "darwin"


def get_platform() -> str:
    """Get current operating system platform
    
    Returns:
        str: Platform name (windows, linux, darwin)
    """
    return platform.system().lower()


def is_windows() -> bool:
    """Check if running on Windows
    
    Returns:
        bool: True if running on Windows, False otherwise
    """
    return get_platform() == PLATFORM_WINDOWS


def is_linux() -> bool:
    """Check if running on Linux
    
    Returns:
        bool: True if running on Linux, False otherwise
    """
    return get_platform() == PLATFORM_LINUX


def is_macos() -> bool:
    """Check if running on macOS
    
    Returns:
        bool: True if running on macOS, False otherwise
    """
    return get_platform() == PLATFORM_MACOS


def get_os_info() -> dict:
    """Get detailed OS information
    
    Returns:
        dict: OS information
    """
    return {
        "platform": get_platform(),
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_compiler": platform.python_compiler()
    }


def check_dependency(cmd: str, args: list = None) -> bool:
    """Check if a dependency is installed
    
    Args:
        cmd: Command to check (e.g., 'nmap', 'sqlmap')
        args: Additional arguments for the command (e.g., ['--version'])
        
    Returns:
        bool: True if dependency is installed, False otherwise
    """
    if args is None:
        args = ["--version"]
    
    try:
        # Build full command
        full_cmd = [cmd] + args
        
        # Execute command
        result = subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            timeout=5
        )
        
        # Return True if command succeeded
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
        return False
    except Exception:
        return False


def find_executable(cmd: str) -> str:
    """Find the full path to an executable
    
    Args:
        cmd: Command name to find
        
    Returns:
        str: Full path to executable or empty string if not found
    """
    # On Windows, check for .exe extension
    if is_windows() and not cmd.endswith(".exe"):
        cmd = f"{cmd}.exe"
    
    # Check PATH environment variable
    for path in os.environ["PATH"].split(os.pathsep):
        exe_path = os.path.join(path, cmd)
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    
    return ""
