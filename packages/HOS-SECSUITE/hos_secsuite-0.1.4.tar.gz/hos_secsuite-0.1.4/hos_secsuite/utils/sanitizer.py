"""Input sanitization and validation utilities"""

import re
from typing import Optional, Any


def sanitize_input(input_str: str, allowed_chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- /\\:;@#$%^&*()+=[]{}|?!~`'") -> str:
    """Sanitize input string by removing potentially dangerous characters
    
    Args:
        input_str: Input string to sanitize
        allowed_chars: String of allowed characters
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(input_str, str):
        return input_str
    
    # Build the sanitized string by including only allowed characters
    sanitized = ""
    for char in input_str:
        if char in allowed_chars:
            sanitized += char
    
    return sanitized


def validate_url(url: str) -> bool:
    """Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    # Basic URL regex pattern
    url_pattern = r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"
    return re.match(url_pattern, url) is not None


def validate_ip(ip: str) -> bool:
    """Validate IP address format (IPv4 or IPv6)
    
    Args:
        ip: IP address to validate
        
    Returns:
        bool: True if IP is valid, False otherwise
    """
    # IPv4 regex pattern
    ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    
    # IPv6 regex pattern (supports compressed format)
    ipv6_pattern = r"^(?:[0-9a-fA-F]{1,4}:){1,7}(?:[0-9a-fA-F]{1,4}|:|::)$|^::1$|^::$"
    
    return re.match(ipv4_pattern, ip) is not None or re.match(ipv6_pattern, ip) is not None


def validate_port(port: Any) -> bool:
    """Validate port number
    
    Args:
        port: Port number to validate (int or str)
        
    Returns:
        bool: True if port is valid, False otherwise
    """
    try:
        port_num = int(port)
        return 0 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def sanitize_command_param(param: str) -> str:
    """Sanitize command parameter to prevent command injection
    
    Args:
        param: Command parameter to sanitize
        
    Returns:
        str: Sanitized parameter
    """
    if not isinstance(param, str):
        return param
    
    # Remove potentially dangerous characters for command injection
    dangerous_chars = ";&|<>(){}[]$`'\"\n\r\t\x00"
    sanitized = ""
    for char in param:
        if char not in dangerous_chars:
            sanitized += char
    
    return sanitized


def sanitize_sql_input(input_str: str) -> str:
    """Sanitize input for SQL queries
    
    Args:
        input_str: Input string to sanitize for SQL
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(input_str, str):
        return input_str
    
    # Remove SQL special characters
    sql_chars = "'\"\\;--#()"
    # Create a regex pattern that matches any of these characters
    pattern = "[" + re.escape(sql_chars) + "]"
    sanitized = re.sub(pattern, "", input_str)
    
    # Remove common SQL keywords that could be used in injection attacks
    sql_keywords = ["OR", "AND", "UNION", "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    for keyword in sql_keywords:
        # Use word boundaries to match whole keywords only
        sanitized = re.sub(rf"\b{keyword}\b", "", sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def sanitize_html(input_str: str) -> str:
    """Sanitize input for HTML output to prevent XSS
    
    Args:
        input_str: Input string to sanitize for HTML
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(input_str, str):
        return input_str
    
    # HTML entity encoding for dangerous characters
    html_entities = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
        "=": "&#x3D;",
        "`": "&#x60;",
        "(": "&#x28;",
        ")": "&#x29;",
        "{": "&#x7B;",
        "}": "&#x7D;",
        "[": "&#x5B;",
        "]": "&#x5D;",
    }
    
    sanitized = input_str
    for char, entity in html_entities.items():
        sanitized = sanitized.replace(char, entity)
    
    return sanitized


def is_valid_filename(filename: str) -> bool:
    """Check if filename is valid (no path traversal)
    
    Args:
        filename: Filename to check
        
    Returns:
        bool: True if filename is valid, False otherwise
    """
    # Check for path traversal attempts
    dangerous_patterns = ["..", "/", "\\", ":", "*", "?", "<", ">", "|"]
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False
    
    # Check for null bytes
    if "\x00" in filename:
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other issues
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove path traversal attempts
    filename = filename.replace("..", "")
    filename = filename.replace("/", "_")
    filename = filename.replace("\\", "_")
    
    # Remove dangerous characters
    filename = re.sub(r"[<>:'\"/\\|?*\x00]", "_", filename)
    
    # Remove leading/trailing whitespace
    filename = filename.strip()
    
    return filename
