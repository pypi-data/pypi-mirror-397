"""Scrapy integration for HOS SecSuite"""

import asyncio
import subprocess
import sys
import os
import tempfile
import json
from typing import Dict, Any, Optional, List

from hos_secsuite.core.base_module import BaseModule


class ScrapyIntegrationModule(BaseModule):
    """Scrapy integration module for advanced web crawling"""
    
    name = "web.request.scrapy"
    description = "Scrapy - Advanced web crawling and scraping framework"
    category = "web"
    subcategory = "request"
    
    options = {
        "start_urls": {
            "required": True,
            "default": [],
            "description": "List of start URLs as JSON string"
        },
        "allowed_domains": {
            "required": False,
            "default": [],
            "description": "List of allowed domains as JSON string"
        },
        "depth": {
            "required": False,
            "default": 1,
            "description": "Maximum crawl depth"
        },
        "follow_links": {
            "required": False,
            "default": True,
            "description": "Follow links in pages"
        },
        "extract_links": {
            "required": False,
            "default": True,
            "description": "Extract links from pages"
        },
        "extract_text": {
            "required": False,
            "default": False,
            "description": "Extract text content from pages"
        },
        "user_agent": {
            "required": False,
            "default": "Scrapy/2.11.0 (+https://scrapy.org)",
            "description": "Custom User-Agent header"
        },
        "proxy": {
            "required": False,
            "default": "",
            "description": "HTTP proxy URL"
        },
        "timeout": {
            "required": False,
            "default": 30,
            "description": "Seconds to wait before timeout"
        },
        "concurrent_requests": {
            "required": False,
            "default": 16,
            "description": "Number of concurrent requests"
        },
        "output_format": {
            "required": False,
            "default": "json",
            "description": "Output format (json, jsonlines, csv, xml)"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run Scrapy to crawl websites
        
        Returns:
            Dict[str, Any]: Module execution result
        """
        start_urls = self.current_options["start_urls"]
        allowed_domains = self.current_options["allowed_domains"]
        depth = self.current_options["depth"]
        follow_links = self.current_options["follow_links"]
        extract_links = self.current_options["extract_links"]
        extract_text = self.current_options["extract_text"]
        user_agent = self.current_options["user_agent"]
        proxy = self.current_options["proxy"]
        timeout = self.current_options["timeout"]
        concurrent_requests = self.current_options["concurrent_requests"]
        output_format = self.current_options["output_format"]
        
        # Convert string options to list if needed
        if isinstance(start_urls, str):
            try:
                start_urls = json.loads(start_urls)
            except Exception:
                return {
                    "status": "error",
                    "message": "Invalid start_urls format. Expected JSON string."
                }
        
        if isinstance(allowed_domains, str):
            try:
                allowed_domains = json.loads(allowed_domains)
            except Exception:
                return {
                    "status": "error",
                    "message": "Invalid allowed_domains format. Expected JSON string."
                }
        
        # Create temporary project directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple Scrapy spider
            spider_code = self._generate_spider_code(
                start_urls,
                allowed_domains,
                depth,
                follow_links,
                extract_links,
                extract_text,
                user_agent,
                proxy,
                timeout
            )
            
            # Write spider to file
            spider_file = os.path.join(temp_dir, "simple_spider.py")
            with open(spider_file, "w") as f:
                f.write(spider_code)
            
            # Write settings file
            settings_code = self._generate_settings(
                concurrent_requests,
                output_format
            )
            settings_file = os.path.join(temp_dir, "settings.py")
            with open(settings_file, "w") as f:
                f.write(settings_code)
            
            # Create output file path
            output_file = os.path.join(temp_dir, f"output.{output_format}")
            
            # Build Scrapy command
            cmd = [
                sys.executable, "-m", "scrapy", "runspider",
                spider_file,
                "--settings", settings_file,
                "-o", output_file
            ]
            
            try:
                # Run Scrapy as a subprocess
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=600  # 10 minutes timeout for Scrapy
                )
                
                # Check if output file exists and read it
                output_data = None
                if os.path.exists(output_file):
                    with open(output_file, "r") as f:
                        if output_format == "json":
                            output_data = json.load(f)
                        else:
                            output_data = f.read()
                
                # Prepare result
                execution_result = {
                    "status": "success" if result.returncode == 0 else "error",
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "command": " ".join(cmd),
                    "output": output_data,
                    "output_format": output_format,
                    "start_urls": start_urls,
                    "allowed_domains": allowed_domains,
                    "depth": depth
                }
                
                return execution_result
            except subprocess.TimeoutExpired:
                return {
                    "status": "error",
                    "message": "Scrapy crawl timed out after 10 minutes",
                    "command": " ".join(cmd)
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to run Scrapy: {str(e)}",
                    "command": " ".join(cmd)
                }
    
    def _generate_spider_code(
        self,
        start_urls: List[str],
        allowed_domains: List[str],
        depth: int,
        follow_links: bool,
        extract_links: bool,
        extract_text: bool,
        user_agent: str,
        proxy: str,
        timeout: int
    ) -> str:
        """Generate Scrapy spider code
        
        Args:
            start_urls: List of start URLs
            allowed_domains: List of allowed domains
            depth: Maximum crawl depth
            follow_links: Whether to follow links
            extract_links: Whether to extract links
            extract_text: Whether to extract text
            user_agent: User-Agent string
            proxy: Proxy URL
            timeout: Timeout in seconds
            
        Returns:
            str: Generated spider code
        """
        return f"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class SimpleSpider(CrawlSpider):
    name = 'simple_spider'
    start_urls = {start_urls!r}
    allowed_domains = {allowed_domains!r}
    max_depth = {depth}
    
    custom_settings = {
        'USER_AGENT': {user_agent!r},
        'DOWNLOAD_TIMEOUT': {timeout},
        'DEPTH_LIMIT': {depth},
        'ROBOTSTXT_OBEY': False,
    }
    
    # Configure proxy if provided
    {f"'HTTPPROXY_ENABLED': True, 'HTTP_PROXY': {proxy!r}, 'HTTPS_PROXY': {proxy!r}," if proxy else ""}
    
    # Define rules
    rules = (
        Rule(
            LinkExtractor(),
            callback='parse_item',
            follow={follow_links!r},
            process_links='process_links'
        ),
    )
    
    def process_links(self, links):
        """Process links before following"""
        return links
    
    def parse_item(self, response):
        """Parse response and extract data"""
        item = {}
        
        # Extract URL and status code
        item['url'] = response.url
        item['status'] = response.status
        item['depth'] = response.meta.get('depth', 0)
        
        # Extract headers
        item['headers'] = dict(response.headers)
        
        # Extract links if enabled
        {f"if {extract_links!r}:
            item['links'] = [link.url for link in LinkExtractor().extract_links(response)]
        "}
        
        # Extract text if enabled
        {f"if {extract_text!r}:
            item['text'] = response.text
        "}
        
        yield item
"""
    
    def _generate_settings(self, concurrent_requests: int, output_format: str) -> str:
        """Generate Scrapy settings
        
        Args:
            concurrent_requests: Number of concurrent requests
            output_format: Output format
            
        Returns:
            str: Generated settings code
        """
        return f"""
# Scrapy settings for simple crawl

BOT_NAME = 'simple_crawler'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

# Configure concurrent requests
CONCURRENT_REQUESTS = {concurrent_requests}
CONCURRENT_REQUESTS_PER_DOMAIN = {concurrent_requests // 2}
CONCURRENT_REQUESTS_PER_IP = {concurrent_requests // 4}

# Configure item pipelines
ITEM_PIPELINES = {
}

# Configure extensions
EXTENSIONS = {
}

# Disable cookies
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Disable logging
LOG_LEVEL = 'WARNING'

# Output encoding
FEED_EXPORT_ENCODING = 'utf-8'

# Configure feed format based on output_format
FEED_FORMAT = '{output_format}'
"""
