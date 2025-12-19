"""XSStrike integration for HOS SecSuite"""

import asyncio
import subprocess
import sys
import os
from typing import Dict, Any, Optional

from hos_secsuite.core.base_module import BaseModule


class XSStrikeModule(BaseModule):
    """XSStrike integration module for XSS detection"""
    
    name = "web.vuln.xsstrike"
    description = "XSStrike - Advanced XSS detection suite with intelligent payload generation"
    category = "web"
    subcategory = "vuln"
    
    options = {
        "target": {
            "required": True,
            "default": "",
            "description": "Target URL with parameter (e.g. 'http://example.com/search?q=test')"
        },
        "method": {
            "required": False,
            "default": "GET",
            "description": "HTTP method (GET, POST)"
        },
        "data": {
            "required": False,
            "default": "",
            "description": "POST data string (e.g. 'q=test&submit=search')"
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
        "threads": {
            "required": False,
            "default": 1,
            "description": "Number of threads to use"
        },
        "timeout": {
            "required": False,
            "default": 30,
            "description": "Seconds to wait before timeout"
        },
        "crawl": {
            "required": False,
            "default": False,
            "description": "Enable crawling"
        },
        "depth": {
            "required": False,
            "default": 2,
            "description": "Crawling depth"
        },
        "blind": {
            "required": False,
            "default": False,
            "description": "Enable blind XSS testing"
        },
        "blind_url": {
            "required": False,
            "default": "",
            "description": "Blind XSS callback URL"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run XSStrike to detect XSS vulnerabilities
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        target = self.current_options["target"]
        method = self.current_options["method"]
        data = self.current_options["data"]
        cookie = self.current_options["cookie"]
        proxy = self.current_options["proxy"]
        threads = self.current_options["threads"]
        timeout = self.current_options["timeout"]
        crawl = self.current_options["crawl"]
        depth = self.current_options["depth"]
        blind = self.current_options["blind"]
        blind_url = self.current_options["blind_url"]
        
        # Check if xsstrike.py exists in current directory or PATH
        xsstrike_path = None
        if os.path.exists("xsstrike.py"):
            xsstrike_path = "./xsstrike.py"
        else:
            # Try to find xsstrike in PATH
            for path in os.environ["PATH"].split(os.pathsep):
                potential_path = os.path.join(path, "xsstrike.py")
                if os.path.exists(potential_path):
                    xsstrike_path = potential_path
                    break
        
        if not xsstrike_path:
            # Fallback: Use git clone to get XSStrike if not found
            return {
                "status": "error",
                "message": "XSStrike not found. Please install it using 'git clone https://github.com/s0md3v/XSStrike'"
            }
        
        # Build XSStrike command
        cmd = [sys.executable, xsstrike_path]
        
        # Add target
        cmd.extend(["-u", target])
        
        # Add HTTP method if POST
        if method == "POST":
            cmd.extend(["--data", data])
        
        # Add cookie if provided
        if cookie:
            cmd.extend(["--cookie", cookie])
        
        # Add proxy if provided
        if proxy:
            cmd.extend(["--proxy", proxy])
        
        # Add other options
        cmd.extend(["--threads", str(threads)])
        cmd.extend(["--timeout", str(timeout)])
        
        # Add crawling options
        if crawl:
            cmd.extend(["--crawl", str(depth)])
        
        # Add blind XSS options
        if blind:
            cmd.append("--blind")
            if blind_url:
                cmd.extend(["--blind-url", blind_url])
        
        # Add output options
        cmd.extend(["--silent", "--no-live-scan"])
        
        try:
            # Run XSStrike as a subprocess
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minutes timeout for XSStrike
            )
            
            # Parse XSStrike output
            output = {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
            
            # Extract vulnerable parameters from output
            vulnerable_params = []
            if "Vulnerable:" in result.stdout:
                for line in result.stdout.split("\n"):
                    if "Vulnerable:" in line:
                        param = line.split(":")[1].strip()
                        if param not in vulnerable_params:
                            vulnerable_params.append(param)
            
            output["vulnerable_parameters"] = vulnerable_params
            
            return output
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "XSStrike scan timed out after 5 minutes",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to run XSStrike: {str(e)}",
                "command": " ".join(cmd)
            }
