"""mitmproxy integration for HOS SecSuite"""

import asyncio
import subprocess
import sys
from typing import Dict, Any, Optional

from hos_secsuite.core.base_module import BaseModule


class MITMProxyModule(BaseModule):
    """mitmproxy integration module"""
    
    name = "web.proxy.mitmproxy"
    description = "MITM Proxy - HTTP/HTTPS interception and modification"
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
            "default": 8080,
            "description": "Proxy listen port"
        },
        "mode": {
            "required": False,
            "default": "regular",
            "description": "Proxy mode (regular, transparent, socks5)"
        },
        "web_interface": {
            "required": False,
            "default": False,
            "description": "Enable web interface"
        },
        "web_port": {
            "required": False,
            "default": 8081,
            "description": "Web interface port"
        },
        "ssl_insecure": {
            "required": False,
            "default": False,
            "description": "Disable SSL verification"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.is_running = False
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run mitmproxy
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        listen_host = self.current_options["listen_host"]
        listen_port = self.current_options["listen_port"]
        mode = self.current_options["mode"]
        web_interface = self.current_options["web_interface"]
        web_port = self.current_options["web_port"]
        ssl_insecure = self.current_options["ssl_insecure"]
        
        # Build mitmproxy command
        cmd = [sys.executable, "-m", "mitmproxy"]
        
        # Add mode
        if mode == "transparent":
            cmd.extend(["--mode", "transparent"])
        elif mode == "socks5":
            cmd.extend(["--mode", "socks5"])
        
        # Add listen address
        cmd.extend(["--listen-host", listen_host])
        cmd.extend(["--listen-port", str(listen_port)])
        
        # Add web interface if enabled
        if web_interface:
            cmd.extend(["--web-host", listen_host])
            cmd.extend(["--web-port", str(web_port)])
        
        # Add SSL insecure if enabled
        if ssl_insecure:
            cmd.append("--ssl-insecure")
        
        try:
            # Start mitmproxy as a subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_running = True
            
            result = {
                "status": "success",
                "message": "mitmproxy started successfully",
                "proxy_url": f"http://{listen_host}:{listen_port}",
                "web_interface_url": f"http://{listen_host}:{web_port}" if web_interface else None,
                "pid": self.process.pid,
                "command": " ".join(cmd)
            }
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start mitmproxy: {str(e)}"
            }
    
    def stop(self) -> Dict[str, Any]:
        """Stop mitmproxy
        
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
                    "message": "mitmproxy stopped successfully"
                }
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.is_running = False
                return {
                    "status": "success",
                    "message": "mitmproxy killed successfully"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to stop mitmproxy: {str(e)}"
                }
        else:
            return {
                "status": "error",
                "message": "mitmproxy is not running"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get mitmproxy status
        
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
