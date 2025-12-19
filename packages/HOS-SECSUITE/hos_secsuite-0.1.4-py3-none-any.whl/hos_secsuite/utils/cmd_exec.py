"""Command execution utilities with security considerations"""

import subprocess
import asyncio
import shlex
from typing import Dict, Any, Optional, List


class CommandResult:
    """Command execution result"""
    
    def __init__(self,
                 returncode: int,
                 stdout: str,
                 stderr: str,
                 command: List[str]):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "command": " ".join(self.command)
        }
    
    def __str__(self) -> str:
        """String representation
        
        Returns:
            str: String representation
        """
        return f"Command: {' '.join(self.command)}\nReturn code: {self.returncode}\nStdout: {self.stdout}\nStderr: {self.stderr}"


def execute_command(
    command: str,
    shell: bool = False,
    timeout: int = 30,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    encoding: str = "utf-8"
) -> CommandResult:
    """Execute a command synchronously with security considerations
    
    Args:
        command: Command to execute
        shell: Whether to use shell (dangerous, use with caution)
        timeout: Command execution timeout in seconds
        cwd: Working directory for command execution
        env: Environment variables for command
        encoding: Output encoding
        
    Returns:
        CommandResult: Command execution result
    
    Raises:
        ValueError: If shell=True and command is not properly sanitized
    """
    # Security warning for shell=True
    if shell:
        raise ValueError("shell=True is dangerous, use shell=False for security")
    
    # Split command string into list if needed
    if isinstance(command, str):
        command_list = shlex.split(command)
    else:
        command_list = command
    
    try:
        # Execute command
        result = subprocess.run(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            timeout=timeout,
            cwd=cwd,
            env=env,
            text=True,
            encoding=encoding
        )
        
        return CommandResult(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            command=command_list
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            returncode=-1,
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            command=command_list
        )
    except Exception as e:
        return CommandResult(
            returncode=-2,
            stdout="",
            stderr=f"Command execution failed: {str(e)}",
            command=command_list
        )


async def execute_async_command(
    command: str,
    shell: bool = False,
    timeout: int = 30,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    encoding: str = "utf-8"
) -> CommandResult:
    """Execute a command asynchronously with security considerations
    
    Args:
        command: Command to execute
        shell: Whether to use shell (dangerous, use with caution)
        timeout: Command execution timeout in seconds
        cwd: Working directory for command execution
        env: Environment variables for command
        encoding: Output encoding
        
    Returns:
        CommandResult: Command execution result
    """
    # Security warning for shell=True
    if shell:
        raise ValueError("shell=True is dangerous, use shell=False for security")
    
    # Split command string into list if needed
    if isinstance(command, str):
        command_list = shlex.split(command)
    else:
        command_list = command
    
    try:
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *command_list,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env
        )
        
        # Wait for process to complete with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            # Terminate process if timeout
            process.terminate()
            await process.wait()
            return CommandResult(
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=command_list
            )
        
        # Decode output
        stdout_str = stdout.decode(encoding) if stdout else ""
        stderr_str = stderr.decode(encoding) if stderr else ""
        
        return CommandResult(
            returncode=process.returncode,
            stdout=stdout_str,
            stderr=stderr_str,
            command=command_list
        )
    except Exception as e:
        return CommandResult(
            returncode=-2,
            stdout="",
            stderr=f"Command execution failed: {str(e)}",
            command=command_list
        )
