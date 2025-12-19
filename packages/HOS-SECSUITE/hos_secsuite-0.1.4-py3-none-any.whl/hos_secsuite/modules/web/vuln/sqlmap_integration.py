"""SQLmap integration for HOS SecSuite"""

import asyncio
import subprocess
import sys
import json
from typing import Dict, Any, Optional

from hos_secsuite.core.base_module import BaseModule


class SQLMapModule(BaseModule):
    """SQLmap integration module for SQL injection detection"""
    
    name = "web.vuln.sqlmap"
    description = "SQLmap - Automated SQL injection detection and exploitation"
    category = "web"
    subcategory = "vuln"
    
    options = {
        "target": {
            "required": True,
            "default": "",
            "description": "Target URL (e.g. 'http://example.com/vuln.php?id=1')"
        },
        "method": {
            "required": False,
            "default": "GET",
            "description": "HTTP method (GET, POST, PUT, DELETE)"
        },
        "data": {
            "required": False,
            "default": "",
            "description": "POST data string (e.g. 'id=1&user=admin')"
        },
        "cookie": {
            "required": False,
            "default": "",
            "description": "HTTP Cookie header value"
        },
        "proxy": {
            "required": False,
            "default": "",
            "description": "Use a proxy (e.g. 'http://127.0.0.1:8080')"
        },
        "timeout": {
            "required": False,
            "default": 30,
            "description": "Seconds to wait before timeout"
        },
        "threads": {
            "required": False,
            "default": 1,
            "description": "Number of concurrent HTTP requests"
        },
        "level": {
            "required": False,
            "default": 1,
            "description": "Test level (1-5)"
        },
        "risk": {
            "required": False,
            "default": 1,
            "description": "Risk level (1-3)"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run SQLmap to detect SQL injection vulnerabilities
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        target = self.current_options["target"]
        method = self.current_options["method"]
        data = self.current_options["data"]
        cookie = self.current_options["cookie"]
        proxy = self.current_options["proxy"]
        timeout = self.current_options["timeout"]
        threads = self.current_options["threads"]
        level = self.current_options["level"]
        risk = self.current_options["risk"]
        
        # Build SQLmap command
        cmd = [sys.executable, "-m", "sqlmap"]
        
        # Add target
        cmd.extend(["-u", target])
        
        # Add HTTP method if not GET
        if method != "GET":
            cmd.extend(["--method", method])
        
        # Add POST data if provided
        if data:
            cmd.extend(["--data", data])
        
        # Add cookie if provided
        if cookie:
            cmd.extend(["--cookie", cookie])
        
        # Add proxy if provided
        if proxy:
            cmd.extend(["--proxy", proxy])
        
        # Add other options
        cmd.extend(["--timeout", str(timeout)])
        cmd.extend(["--threads", str(threads)])
        cmd.extend(["--level", str(level)])
        cmd.extend(["--risk", str(risk)])
        
        # Add output options
        cmd.extend(["--batch", "--random-agent"])
        cmd.extend(["--output-format", "json"])
        cmd.extend(["--output-dir", "/tmp/sqlmap_output"])
        
        try:
            # Run SQLmap as a subprocess
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minutes timeout for sqlmap
            )
            
            # Parse sqlmap output
            output = {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
            
            # Extract vulnerable parameters from output
            vulnerable_params = []
            if "Parameter: " in result.stdout:
                # Simple parsing for vulnerable parameters
                for line in result.stdout.split("\n"):
                    if line.startswith("Parameter: "):
                        param = line.split(" ")[1]
                        if param not in vulnerable_params:
                            vulnerable_params.append(param)
            
            output["vulnerable_parameters"] = vulnerable_params
            
            return output
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "SQLmap scan timed out after 5 minutes",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to run SQLmap: {str(e)}",
                "command": " ".join(cmd)
            }
