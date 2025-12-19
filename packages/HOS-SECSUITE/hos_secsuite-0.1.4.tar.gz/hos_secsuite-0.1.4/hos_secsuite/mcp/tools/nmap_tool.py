"""Nmap tool integration for MCP Service"""

import subprocess
import json
from typing import Dict, Any, Optional, List

from hos_secsuite.core.base_module import BaseModule


class NmapTool(BaseModule):
    """Nmap tool integration module"""
    
    name = "scan.nmap"
    description = "Nmap - Network scanning and discovery tool"
    category = "scan"
    subcategory = "network"
    
    options = {
        "target": {
            "required": True,
            "default": "",
            "description": "Target IP address or range (e.g., '192.168.1.1' or '192.168.1.0/24')"
        },
        "ports": {
            "required": False,
            "default": "1-1000",
            "description": "Port range to scan (e.g., '1-1000' or '22,80,443')"
        },
        "scan_type": {
            "required": False,
            "default": "tcp",
            "description": "Scan type (tcp, udp, syn, connect)"
        },
        "os_detection": {
            "required": False,
            "default": False,
            "description": "Enable OS detection (-O)"
        },
        "service_version": {
            "required": False,
            "default": False,
            "description": "Enable service version detection (-sV)"
        },
        "script_scan": {
            "required": False,
            "default": False,
            "description": "Enable script scanning (-sC)"
        },
        "timing_template": {
            "required": False,
            "default": "3",
            "description": "Timing template (0-5, where 0 is slowest and 5 is fastest)"
        },
        "output_format": {
            "required": False,
            "default": "json",
            "description": "Output format (json, xml, grepable)"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run nmap scan
        
        Returns:
            Dict[str, Any]: Nmap scan result
        """
        target = self.current_options["target"]
        ports = self.current_options["ports"]
        scan_type = self.current_options["scan_type"]
        os_detection = self.current_options["os_detection"]
        service_version = self.current_options["service_version"]
        script_scan = self.current_options["script_scan"]
        timing_template = self.current_options["timing_template"]
        output_format = self.current_options["output_format"]
        
        # Build nmap command
        cmd = ["nmap"]
        
        # Add scan type
        if scan_type == "syn":
            cmd.append("-sS")
        elif scan_type == "connect":
            cmd.append("-sT")
        elif scan_type == "udp":
            cmd.append("-sU")
        
        # Add port range
        cmd.extend(["-p", ports])
        
        # Add OS detection if enabled
        if os_detection:
            cmd.append("-O")
        
        # Add service version detection if enabled
        if service_version:
            cmd.append("-sV")
        
        # Add script scanning if enabled
        if script_scan:
            cmd.append("-sC")
        
        # Add timing template
        cmd.extend(["-T", timing_template])
        
        # Add output format
        cmd.extend(["-oX", "-"] if output_format == "xml" else ["-oG", "-"] if output_format == "grepable" else ["-o", "-"], "-" if output_format == "json" else ""])
        
        # Add target
        cmd.append(target)
        
        try:
            # Run nmap as a subprocess
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600  # 10 minutes timeout for nmap
            )
            
            # Parse output based on format
            output = {}
            if output_format == "json":
                # Nmap json output needs special handling
                # Use -oX for XML and convert to json, or use --script to output json
                # For simplicity, we'll use XML and convert to dict
                cmd = ["nmap", "-oX", "-", target]
                xml_result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output = {"xml_output": xml_result.stdout}
            else:
                output = {f"{output_format}_output": result.stdout}
            
            return {
                "status": "success",
                "command": " ".join(cmd),
                "result": output,
                "target": target,
                "scan_type": scan_type,
                "ports": ports
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Nmap scan timed out after 10 minutes",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to run nmap: {str(e)}",
                "command": " ".join(cmd)
            }
    
    async def port_scan(self, target: str, ports: str = "1-1000", **kwargs) -> Dict[str, Any]:
        """Perform port scan
        
        Args:
            target: Target IP address or range
            ports: Port range to scan
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Scan result
        """
        return await self._run_scan(target, ports, scan_type="tcp", **kwargs)
    
    async def os_detection(self, target: str, **kwargs) -> Dict[str, Any]:
        """Perform OS detection
        
        Args:
            target: Target IP address
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: OS detection result
        """
        return await self._run_scan(target, ports="1-1000", scan_type="tcp", os_detection=True, **kwargs)
    
    async def service_version(self, target: str, **kwargs) -> Dict[str, Any]:
        """Perform service version detection
        
        Args:
            target: Target IP address
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Service version detection result
        """
        return await self._run_scan(target, ports="1-1000", scan_type="tcp", service_version=True, **kwargs)
    
    async def _run_scan(self, target: str, ports: str, scan_type: str, **kwargs) -> Dict[str, Any]:
        """Helper method to run scan
        
        Args:
            target: Target IP address or range
            ports: Port range to scan
            scan_type: Scan type
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Scan result
        """
        # Update options
        self.set_option("target", target)
        self.set_option("ports", ports)
        self.set_option("scan_type", scan_type)
        
        for key, value in kwargs.items():
            if key in self.options:
                self.set_option(key, value)
        
        # Run the scan
        return await self.run()
