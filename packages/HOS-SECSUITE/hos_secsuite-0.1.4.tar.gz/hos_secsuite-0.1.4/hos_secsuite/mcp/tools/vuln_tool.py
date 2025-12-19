"""Vulnerability scanning tool integration for MCP Service"""

import asyncio
import subprocess
import json
from typing import Dict, Any, Optional, List

from hos_secsuite.core.base_module import BaseModule


class VulnTool(BaseModule):
    """Vulnerability scanning tool integration module"""
    
    name = "web.vuln"
    description = "Vulnerability scanning tools collection"
    category = "web"
    subcategory = "vuln"
    
    options = {
        "target": {
            "required": True,
            "default": "",
            "description": "Target URL or IP address"
        },
        "scan_type": {
            "required": True,
            "default": "sql_injection",
            "description": "Vulnerability type to scan for (sql_injection, xss, dir_brute)",
            "choices": ["sql_injection", "xss", "dir_brute"]
        },
        "proxy": {
            "required": False,
            "default": "",
            "description": "HTTP proxy URL for scanning"
        },
        "timeout": {
            "required": False,
            "default": 300,
            "description": "Scan timeout in seconds"
        },
        "threads": {
            "required": False,
            "default": 10,
            "description": "Number of threads to use"
        },
        "depth": {
            "required": False,
            "default": 1,
            "description": "Scan depth (for recursive scanning)"
        },
        "wordlist": {
            "required": False,
            "default": "",
            "description": "Custom wordlist path (for dir_brute)"
        },
        "extensions": {
            "required": False,
            "default": "php,html,js,css,txt",
            "description": "File extensions to scan for (for dir_brute)"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run vulnerability scan
        
        Returns:
            Dict[str, Any]: Scan result
        """
        target = self.current_options["target"]
        scan_type = self.current_options["scan_type"]
        proxy = self.current_options["proxy"]
        timeout = self.current_options["timeout"]
        threads = self.current_options["threads"]
        depth = self.current_options["depth"]
        wordlist = self.current_options["wordlist"]
        extensions = self.current_options["extensions"]
        
        # Select scan type
        if scan_type == "sql_injection":
            return await self._sql_injection_scan(target, proxy, timeout, threads)
        elif scan_type == "xss":
            return await self._xss_scan(target, proxy, timeout, threads, depth)
        elif scan_type == "dir_brute":
            return await self._dir_brute_scan(target, proxy, timeout, threads, wordlist, extensions)
        else:
            return {
                "status": "error",
                "message": f"Unknown scan type: {scan_type}",
                "scan_type": scan_type
            }
    
    async def _sql_injection_scan(self, target: str, proxy: str, timeout: int, threads: int) -> Dict[str, Any]:
        """Run SQL injection scan
        
        Args:
            target: Target URL
            proxy: Proxy URL
            timeout: Timeout in seconds
            threads: Number of threads
            
        Returns:
            Dict[str, Any]: SQL injection scan result
        """
        try:
            # Use sqlmap for SQL injection scanning
            cmd = [
                "sqlmap", "-u", target,
                "--batch", "--random-agent",
                "--timeout", str(timeout),
                "--threads", str(threads),
                "--output-format", "json",
                "--output-dir", "/tmp/sqlmap_output"
            ]
            
            # Add proxy if provided
            if proxy:
                cmd.extend(["--proxy", proxy])
            
            # Run sqlmap
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout + 60  # Add extra timeout for process
            )
            
            return {
                "status": "success",
                "scan_type": "sql_injection",
                "target": target,
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "scan_type": "sql_injection",
                "message": "SQL injection scan timed out",
                "target": target
            }
        except Exception as e:
            return {
                "status": "error",
                "scan_type": "sql_injection",
                "message": f"Failed to run SQL injection scan: {str(e)}",
                "target": target
            }
    
    async def _xss_scan(self, target: str, proxy: str, timeout: int, threads: int, depth: int) -> Dict[str, Any]:
        """Run XSS scan
        
        Args:
            target: Target URL
            proxy: Proxy URL
            timeout: Timeout in seconds
            threads: Number of threads
            depth: Crawling depth
            
        Returns:
            Dict[str, Any]: XSS scan result
        """
        try:
            # Use XSStrike for XSS scanning
            cmd = [
                "python", "-m", "xsstrike", "-u", target,
                "--threads", str(threads),
                "--timeout", str(timeout),
                "--silent", "--no-live-scan"
            ]
            
            # Add crawling if depth > 1
            if depth > 1:
                cmd.extend(["--crawl", str(depth)])
            
            # Add proxy if provided
            if proxy:
                cmd.extend(["--proxy", proxy])
            
            # Run XSStrike
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout + 60  # Add extra timeout for process
            )
            
            return {
                "status": "success",
                "scan_type": "xss",
                "target": target,
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "scan_type": "xss",
                "message": "XSS scan timed out",
                "target": target
            }
        except Exception as e:
            return {
                "status": "error",
                "scan_type": "xss",
                "message": f"Failed to run XSS scan: {str(e)}",
                "target": target
            }
    
    async def _dir_brute_scan(self, target: str, proxy: str, timeout: int, threads: int, wordlist: str, extensions: str) -> Dict[str, Any]:
        """Run directory brute-force scan
        
        Args:
            target: Target URL
            proxy: Proxy URL
            timeout: Timeout in seconds
            threads: Number of threads
            wordlist: Custom wordlist path
            extensions: File extensions to scan for
            
        Returns:
            Dict[str, Any]: Directory brute-force scan result
        """
        try:
            # Use dirsearch for directory brute-forcing
            cmd = [
                "python", "-m", "dirsearch", "-u", target,
                "-t", str(threads),
                "--timeout", str(timeout),
                "-e", extensions,
                "--json-report", "/tmp/dirsearch_report.json"
            ]
            
            # Add custom wordlist if provided
            if wordlist:
                cmd.extend(["-w", wordlist])
            
            # Add proxy if provided
            if proxy:
                cmd.extend(["--proxy", proxy])
            
            # Run dirsearch
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout + 60  # Add extra timeout for process
            )
            
            return {
                "status": "success",
                "scan_type": "dir_brute",
                "target": target,
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "scan_type": "dir_brute",
                "message": "Directory brute-force scan timed out",
                "target": target
            }
        except Exception as e:
            return {
                "status": "error",
                "scan_type": "dir_brute",
                "message": f"Failed to run directory brute-force scan: {str(e)}",
                "target": target
            }
    
    async def sql_injection_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Run SQL injection scan
        
        Args:
            target: Target URL
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: SQL injection scan result
        """
        self.set_option("target", target)
        self.set_option("scan_type", "sql_injection")
        
        # Update options from kwargs
        for key, value in kwargs.items():
            if key in self.options:
                self.set_option(key, value)
        
        return await self.run()
    
    async def xss_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Run XSS scan
        
        Args:
            target: Target URL
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: XSS scan result
        """
        self.set_option("target", target)
        self.set_option("scan_type", "xss")
        
        # Update options from kwargs
        for key, value in kwargs.items():
            if key in self.options:
                self.set_option(key, value)
        
        return await self.run()
    
    async def dir_brute_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Run directory brute-force scan
        
        Args:
            target: Target URL
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Directory brute-force scan result
        """
        self.set_option("target", target)
        self.set_option("scan_type", "dir_brute")
        
        # Update options from kwargs
        for key, value in kwargs.items():
            if key in self.options:
                self.set_option(key, value)
        
        return await self.run()
