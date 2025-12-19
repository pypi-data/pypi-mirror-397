"""Proxy.py integration for HOS SecSuite"""

import asyncio
import subprocess
import sys
from typing import Dict, Any, Optional

from hos_secsuite.core.base_module import BaseModule


class ProxyPyModule(BaseModule):
    """Proxy.py integration module"""
    
    name = "web.proxy.proxypy"
    description = "Proxy.py - Lightweight HTTP proxy framework"
    category = "web"
    subcategory = "proxy"
    
    options = {
        "listen_host": {
            "required": False,
            "default": "127.0.0.1",
            "description": "Proxy listen address"
        },
        "listen_port": {
            "required": False,
            "default": 8888,
            "description": "Proxy listen port"
        },
        "backlog": {
            "required": False,
            "default": 128,
            "description": "TCP backlog"
        },
        "workers": {
            "required": False,
            "default": 1,
            "description": "Number of worker processes"
        },
        "threads": {
            "required": False,
            "default": 5,
            "description": "Number of threads per worker"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.is_running = False
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run Proxy.py
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        listen_host = self.current_options["listen_host"]
        listen_port = self.current_options["listen_port"]
        backlog = self.current_options["backlog"]
        workers = self.current_options["workers"]
        threads = self.current_options["threads"]
        
        # Build Proxy.py command
        cmd = [sys.executable, "-m", "proxy"]
        
        # Add listen address and port
        cmd.extend(["--hostname", listen_host])
        cmd.extend(["--port", str(listen_port)])
        
        # Add other options
        cmd.extend(["--backlog", str(backlog)])
        cmd.extend(["--workers", str(workers)])
        cmd.extend(["--threads", str(threads)])
        
        try:
            # Start Proxy.py as a subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_running = True
            
            result = {
                "status": "success",
                "message": "Proxy.py started successfully",
                "proxy_url": f"http://{listen_host}:{listen_port}",
                "pid": self.process.pid,
                "command": " ".join(cmd)
            }
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start Proxy.py: {str(e)}"
            }
    
    def stop(self) -> Dict[str, Any]:
        """Stop Proxy.py
        
        Returns:
            Dict[str, Any]: Stop result
        """
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.is_running = False
                return {
                    "status": "success",
                    "message": "Proxy.py stopped successfully"
                }
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.is_running = False
                return {
                    "status": "success",
                    "message": "Proxy.py killed successfully"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to stop Proxy.py: {str(e)}"
                }
        else:
            return {
                "status": "error",
                "message": "Proxy.py is not running"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get Proxy.py status
        
        Returns:
            Dict[str, Any]: Status information
        """
        if self.process and self.is_running:
            try:
                # Check if process is still running
                self.process.poll()
                if self.process.returncode is not None:
                    self.is_running = False
                    return {
                        "status": "stopped",
                        "return_code": self.process.returncode
                    }
                
                return {
                    "status": "running",
                    "pid": self.process.pid
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
        else:
            return {
                "status": "stopped"
            }
