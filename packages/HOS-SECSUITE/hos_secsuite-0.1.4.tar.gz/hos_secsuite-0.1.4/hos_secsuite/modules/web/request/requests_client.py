"""requests client integration for HOS SecSuite"""

import asyncio
import requests
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup

from hos_secsuite.core.base_module import BaseModule


class RequestsClientModule(BaseModule):
    """Requests client module for HTTP requests"""
    
    name = "web.request.requests"
    description = "Requests - HTTP client for making HTTP requests"
    category = "web"
    subcategory = "request"
    
    options = {
        "url": {
            "required": True,
            "default": "",
            "description": "Target URL (e.g. 'http://example.com')"
        },
        "method": {
            "required": False,
            "default": "GET",
            "description": "HTTP method (GET, POST, PUT, DELETE, HEAD, OPTIONS)"
        },
        "headers": {
            "required": False,
            "default": {},
            "description": "HTTP headers as JSON string"
        },
        "params": {
            "required": False,
            "default": {},
            "description": "URL parameters as JSON string"
        },
        "data": {
            "required": False,
            "default": {},
            "description": "Request body data as JSON string"
        },
        "json": {
            "required": False,
            "default": {},
            "description": "Request body JSON as JSON string"
        },
        "cookies": {
            "required": False,
            "default": {},
            "description": "Cookies as JSON string"
        },
        "timeout": {
            "required": False,
            "default": 30,
            "description": "Seconds to wait before timeout"
        },
        "verify": {
            "required": False,
            "default": True,
            "description": "Verify SSL certificates"
        },
        "allow_redirects": {
            "required": False,
            "default": True,
            "description": "Allow redirects"
        },
        "proxy": {
            "required": False,
            "default": "",
            "description": "HTTP proxy URL"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Make HTTP request using requests library
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        url = self.current_options["url"]
        method = self.current_options["method"].upper()
        headers = self.current_options["headers"]
        params = self.current_options["params"]
        data = self.current_options["data"]
        json_data = self.current_options["json"]
        cookies = self.current_options["cookies"]
        timeout = self.current_options["timeout"]
        verify = self.current_options["verify"]
        allow_redirects = self.current_options["allow_redirects"]
        proxy = self.current_options["proxy"]
        
        # Convert string options to dict if needed
        if isinstance(headers, str):
            import json
            headers = json.loads(headers)
        
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        if isinstance(data, str):
            import json
            data = json.loads(data)
        
        if isinstance(json_data, str):
            import json
            json_data = json.loads(json_data)
        
        if isinstance(cookies, str):
            import json
            cookies = json.loads(cookies)
        
        # Prepare proxy configuration
        proxies = None
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy
            }
        
        try:
            # Make HTTP request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                cookies=cookies,
                timeout=timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # Parse response content
            content_type = response.headers.get("Content-Type", "")
            
            # Try to parse JSON if content type is JSON
            response_json = None
            if "application/json" in content_type:
                try:
                    response_json = response.json()
                except Exception:
                    pass
            
            # Try to parse HTML if content type is HTML
            response_html = None
            if "text/html" in content_type:
                try:
                    response_html = BeautifulSoup(response.text, "html.parser")
                except Exception:
                    pass
            
            # Extract links from HTML if available
            links = []
            if response_html:
                for a_tag in response_html.find_all("a", href=True):
                    links.append(a_tag["href"])
            
            # Prepare result
            result = {
                "status": "success",
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "cookies": dict(response.cookies),
                "encoding": response.encoding,
                "content_length": len(response.content),
                "text": response.text,
                "json": response_json,
                "links": links,
                "response_time": response.elapsed.total_seconds()
            }
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to make HTTP request: {str(e)}",
                "url": url,
                "method": method
            }
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request
        
        Args:
            url: Target URL
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Request result
        """
        return await self._make_request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make POST request
        
        Args:
            url: Target URL
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Request result
        """
        return await self._make_request("POST", url, **kwargs)
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Helper method to make HTTP request
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Request result
        """
        # Update options with provided arguments
        self.set_option("url", url)
        self.set_option("method", method)
        
        for key, value in kwargs.items():
            if key in self.options:
                self.set_option(key, value)
        
        # Run the module
        return await self.run()
