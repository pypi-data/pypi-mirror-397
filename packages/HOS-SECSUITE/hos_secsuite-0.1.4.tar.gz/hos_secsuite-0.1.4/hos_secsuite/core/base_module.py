"""Base Module class for all HOS SecSuite modules"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseModule(ABC):
    """Base class for all modules in HOS SecSuite
    
    Attributes:
        name: Module name in format 'category.subcategory.module'
        description: Brief description of the module
        options: Default options for the module
        requires_root: Whether the module requires root/admin privileges
        category: Module category (scan, web, info, etc.)
        subcategory: Module subcategory (proxy, vuln, request, etc.)
    """
    
    name: str = "module.name"
    description: str = "Module description"
    options: Dict[str, Any] = {}
    requires_root: bool = False
    category: str = "general"
    subcategory: str = "general"
    
    def __init__(self):
        """Initialize the module"""
        self.current_options = self.options.copy()
    
    def validate_options(self, opts: Optional[Dict[str, Any]] = None) -> bool:
        """Validate module options
        
        Args:
            opts: Options to validate
            
        Returns:
            bool: True if options are valid, False otherwise
        """
        if opts is None:
            opts = self.current_options
        
        # Basic validation - check required options
        for opt_name, opt_config in self.options.items():
            if opt_config.get('required', False) and opt_name not in opts:
                return False
        
        return True
    
    def set_option(self, name: str, value: Any) -> bool:
        """Set a module option
        
        Args:
            name: Option name
            value: Option value
            
        Returns:
            bool: True if option was set successfully, False otherwise
        """
        if name in self.options:
            self.current_options[name] = value
            return True
        return False
    
    def get_options(self) -> Dict[str, Any]:
        """Get current module options
        
        Returns:
            Dict[str, Any]: Current options
        """
        return self.current_options.copy()
    
    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the module
        
        Args:
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Module execution result
        """
        pass
