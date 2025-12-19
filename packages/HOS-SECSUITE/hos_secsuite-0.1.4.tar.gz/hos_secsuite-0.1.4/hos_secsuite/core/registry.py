"""Module Registry for HOS SecSuite"""

import os
import sys
import importlib
from typing import Dict, List, Type
from hos_secsuite.core.base_module import BaseModule


class ModuleRegistry:
    """Module registry to manage and discover modules"""
    
    def __init__(self):
        self.modules: Dict[str, Type[BaseModule]] = {}
        self.module_categories: Dict[str, Dict[str, List[str]]] = {}
    
    def register_module(self, module_class: Type[BaseModule]) -> bool:
        """Register a module class
        
        Args:
            module_class: Module class to register
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        module_name = module_class.name
        if module_name in self.modules:
            return False
        
        self.modules[module_name] = module_class
        
        # Update category structure
        category = module_class.category
        subcategory = module_class.subcategory
        
        if category not in self.module_categories:
            self.module_categories[category] = {}
        
        if subcategory not in self.module_categories[category]:
            self.module_categories[category][subcategory] = []
        
        if module_name not in self.module_categories[category][subcategory]:
            self.module_categories[category][subcategory].append(module_name)
        
        return True
    
    def get_module(self, name: str) -> Type[BaseModule]:
        """Get a module by name
        
        Args:
            name: Module name
            
        Returns:
            Type[BaseModule]: Module class
            
        Raises:
            KeyError: If module not found
        """
        return self.modules[name]
    
    def get_modules(self, category: str = None, subcategory: str = None) -> List[str]:
        """Get modules by category and subcategory
        
        Args:
            category: Module category
            subcategory: Module subcategory
            
        Returns:
            List[str]: List of module names
        """
        if category is None:
            return list(self.modules.keys())
        
        if category not in self.module_categories:
            return []
        
        if subcategory is None:
            all_modules = []
            for subcat_modules in self.module_categories[category].values():
                all_modules.extend(subcat_modules)
            return all_modules
        
        return self.module_categories[category].get(subcategory, [])
    
    def scan_modules(self, path: str = None) -> int:
        """Scan for modules in the given path
        
        Args:
            path: Path to scan for modules
            
        Returns:
            int: Number of modules found
        """
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "..", "modules")
        
        # Add the base path to sys.path if not already present
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        modules_found = 0
        
        # Walk through the modules directory
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    # Calculate module import path
                    rel_path = os.path.relpath(root, base_path)
                    module_path = rel_path.replace(os.sep, ".") + "." + file[:-3]
                    
                    try:
                        # Import the module
                        module = importlib.import_module(module_path)
                        
                        # Find all BaseModule subclasses in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type) and \
                               issubclass(attr, BaseModule) and \
                               attr != BaseModule:
                                # Register the module
                                if self.register_module(attr):
                                    modules_found += 1
                    except Exception as e:
                        print(f"Error importing module {module_path}: {e}")
        
        return modules_found
    
    def list_categories(self) -> List[str]:
        """List all module categories
        
        Returns:
            List[str]: List of categories
        """
        return list(self.module_categories.keys())
    
    def list_subcategories(self, category: str) -> List[str]:
        """List subcategories for a given category
        
        Args:
            category: Module category
            
        Returns:
            List[str]: List of subcategories
        """
        if category not in self.module_categories:
            return []
        return list(self.module_categories[category].keys())
