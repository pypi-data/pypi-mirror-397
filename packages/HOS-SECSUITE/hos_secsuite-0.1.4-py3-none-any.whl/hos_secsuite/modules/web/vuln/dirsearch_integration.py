"""dirsearch integration for HOS SecSuite"""

import asyncio
import subprocess
import sys
import os
from typing import Dict, Any, Optional

from hos_secsuite.core.base_module import BaseModule


class DirSearchModule(BaseModule):
    """dirsearch integration module for directory brute-forcing"""
    
    name = "web.vuln.dirsearch"
    description = "DirSearch - Web path scanner and directory brute-forcing tool"
    category = "web"
    subcategory = "vuln"
    
    options = {
        "target": {
            "required": True,
            "default": "",
            "description": "Target URL (e.g. 'http://example.com')"
        },
        "wordlist": {
            "required": False,
            "default": "",
            "description": "Path to custom wordlist file"
        },
        "extensions": {
            "required": False,
            "default": "php,html,js,css,txt",
            "description": "File extensions to search for"
        },
        "threads": {
            "required": False,
            "default": 10,
            "description": "Number of threads to use"
        },
        "timeout": {
            "required": False,
            "default": 30,
            "description": "Seconds to wait before timeout"
        },
        "proxy": {
            "required": False,
            "default": "",
            "description": "Use a proxy (e.g. 'http://127.0.0.1:8080')"
        },
        "cookie": {
            "required": False,
            "default": "",
            "description": "HTTP Cookie header value"
        },
        "depth": {
            "required": False,
            "default": 1,
            "description": "Maximum recursion depth"
        },
        "exclude_status": {
            "required": False,
            "default": "404",
            "description": "Exclude status codes (comma-separated)"
        },
        "user_agent": {
            "required": False,
            "default": "",
            "description": "Custom User-Agent header"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run dirsearch to discover hidden files and directories
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        target = self.current_options["target"]
        wordlist = self.current_options["wordlist"]
        extensions = self.current_options["extensions"]
        threads = self.current_options["threads"]
        timeout = self.current_options["timeout"]
        proxy = self.current_options["proxy"]
        cookie = self.current_options["cookie"]
        depth = self.current_options["depth"]
        exclude_status = self.current_options["exclude_status"]
        user_agent = self.current_options["user_agent"]
        
        # Check if dirsearch is installed
        dirsearch_path = None
        try:
            # Try to run dirsearch to check if it's installed
            subprocess.run(
                [sys.executable, "-m", "dirsearch", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            dirsearch_path = "dirsearch"
        except subprocess.CalledProcessError:
            # Try to find dirsearch in PATH
            for path in os.environ["PATH"].split(os.pathsep):
                potential_path = os.path.join(path, "dirsearch")
                if os.path.exists(potential_path):
                    dirsearch_path = potential_path
                    break
        except Exception:
            pass
        
        if not dirsearch_path:
            return {
                "status": "error",
                "message": "DirSearch not found. Please install it using 'pip install dirsearch'"
            }
        
        # Build dirsearch command
        cmd = [sys.executable, "-m", dirsearch_path]
        
        # Add target
        cmd.extend(["-u", target])
        
        # Add custom wordlist if provided
        if wordlist and os.path.exists(wordlist):
            cmd.extend(["-w", wordlist])
        
        # Add extensions
        cmd.extend(["-e", extensions])
        
        # Add other options
        cmd.extend(["-t", str(threads)])
        cmd.extend(["--timeout", str(timeout)])
        cmd.extend(["--depth", str(depth)])
        cmd.extend(["--exclude-status", exclude_status])
        
        # Add proxy if provided
        if proxy:
            cmd.extend(["--proxy", proxy])
        
        # Add cookie if provided
        if cookie:
            cmd.extend(["--cookie", cookie])
        
        # Add custom User-Agent if provided
        if user_agent:
            cmd.extend(["-a", user_agent])
        
        # Add output options
        cmd.extend(["--json-report", "/tmp/dirsearch_report.json"])
        
        try:
            # Run dirsearch as a subprocess
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600  # 10 minutes timeout for dirsearch
            )
            
            # Parse dirsearch output
            output = {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
            
            # Extract found paths from output
            found_paths = []
            if "Found:" in result.stdout:
                for line in result.stdout.split("\n"):
                    if "Found:" in line:
                        # Extract path from line like "[200]  /admin.php - 1234 bytes"
                        parts = line.split()
                        if len(parts) >= 3:
                            path = parts[2]
                            found_paths.append(path)
            
            output["found_paths"] = found_paths
            
            return output
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "DirSearch scan timed out after 10 minutes",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to run DirSearch: {str(e)}",
                "command": " ".join(cmd)
            }
