"""Tests for utility functions"""

import pytest
import sys
import logging
from hos_secsuite.utils import (
    get_platform, is_windows, is_linux, is_macos,
    get_os_info, check_dependency,
    execute_command, execute_async_command,
    get_logger,
    sanitize_input, validate_url, validate_ip, validate_port,
    sanitize_command_param, sanitize_sql_input, sanitize_html,
    is_valid_filename, sanitize_filename
)


class TestOSUtils:
    """Tests for OS utility functions"""
    
    def test_get_platform(self):
        """Test getting current platform"""
        platform = get_platform()
        assert platform in ["windows", "linux", "darwin"]
    
    def test_platform_checks(self):
        """Test platform check functions"""
        platform = get_platform()
        
        assert is_windows() == (platform == "windows")
        assert is_linux() == (platform == "linux")
        assert is_macos() == (platform == "darwin")
    
    def test_get_os_info(self):
        """Test getting OS information"""
        os_info = get_os_info()
        assert isinstance(os_info, dict)
        assert "platform" in os_info
        assert "system" in os_info
        assert "python_version" in os_info
    
    def test_check_dependency(self):
        """Test checking dependency"""
        # Check for Python executable which should always be available
        result = check_dependency(sys.executable, ["--version"])
        assert result is True
        
        # Check for non-existent command
        result = check_dependency("non_existent_command")
        assert result is False


class TestCommandUtils:
    """Tests for command execution utility functions"""
    
    def test_execute_command(self):
        """Test executing command synchronously"""
        # Execute a simple command
        result = execute_command([sys.executable, "--version"])
        assert result.returncode == 0
        assert "Python" in result.stdout
    
    def test_execute_invalid_command(self):
        """Test executing invalid command"""
        result = execute_command(["non_existent_command"])
        assert result.returncode != 0
    
    @pytest.mark.asyncio
    async def test_execute_async_command(self):
        """Test executing command asynchronously"""
        result = await execute_async_command([sys.executable, "--version"])
        assert result.returncode == 0
        assert "Python" in result.stdout


class TestLoggerUtils:
    """Tests for logging utility functions"""
    
    def test_get_logger(self):
        """Test getting logger instance"""
        logger = get_logger("test_logger", level=logging.DEBUG)
        assert logger is not None
        
        # Test logging methods
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_get_existing_logger(self):
        """Test getting existing logger instance"""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        assert logger1 is logger2


class TestSanitizerUtils:
    """Tests for input sanitization utility functions"""
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        # Test with normal input
        input_str = "test input"
        sanitized = sanitize_input(input_str)
        assert sanitized == input_str
        
        # Test with dangerous input
        input_str = "test <script>alert('xss')</script> input"
        sanitized = sanitize_input(input_str)
        assert "<script>" not in sanitized
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com/path") is True
        assert validate_url("example.com") is True
        
        # Invalid URLs
        assert validate_url("invalid-url") is False
        assert validate_url("http://") is False
    
    def test_validate_ip(self):
        """Test IP validation"""
        # Valid IPs
        assert validate_ip("127.0.0.1") is True
        assert validate_ip("255.255.255.255") is True
        assert validate_ip("::1") is True
        
        # Invalid IPs
        assert validate_ip("invalid-ip") is False
        assert validate_ip("256.0.0.1") is False
        assert validate_ip("192.168.1") is False
    
    def test_validate_port(self):
        """Test port validation"""
        # Valid ports
        assert validate_port(80) is True
        assert validate_port(443) is True
        assert validate_port(8080) is True
        assert validate_port(65535) is True
        
        # Invalid ports
        assert validate_port("invalid") is False
        assert validate_port(-1) is False
        assert validate_port(65536) is False
    
    def test_sanitize_command_param(self):
        """Test command parameter sanitization"""
        # Test with dangerous command parameter
        param = "test; rm -rf /"
        sanitized = sanitize_command_param(param)
        assert ";" not in sanitized
        # The sanitizer only removes dangerous characters, not entire commands
        assert "rm" in sanitized
        assert "-rf" in sanitized
    
    def test_sanitize_sql_input(self):
        """Test SQL input sanitization"""
        # Test with SQL injection
        sql_input = "' OR '1'='1"
        sanitized = sanitize_sql_input(sql_input)
        assert "'" not in sanitized
        assert "OR" not in sanitized
    
    def test_sanitize_html(self):
        """Test HTML sanitization"""
        # Test with XSS input
        html_input = "<script>alert('xss')</script>"
        sanitized = sanitize_html(html_input)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
    
    def test_filename_validation(self):
        """Test filename validation"""
        # Valid filenames
        assert is_valid_filename("test.txt") is True
        assert is_valid_filename("file123.pdf") is True
        
        # Invalid filenames
        assert is_valid_filename("../test.txt") is False
        assert is_valid_filename("/etc/passwd") is False
        assert is_valid_filename("file*name.txt") is False
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test with dangerous filename
        filename = "../dangerous/filename.txt"
        sanitized = sanitize_filename(filename)
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "_dangerous_filename.txt" in sanitized
