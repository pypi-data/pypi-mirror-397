"""Tests for core modules"""

import pytest
from hos_secsuite.core.base_module import BaseModule
from hos_secsuite.core.registry import ModuleRegistry
from hos_secsuite.core.runner import ModuleRunner


class TestModule(BaseModule):
    """Test module for testing base module functionality"""
    
    name = "test.module"
    description = "Test module"
    category = "test"
    subcategory = "test"
    
    options = {
        "test_option": {
            "required": True,
            "default": "default_value",
            "description": "Test option"
        },
        "optional_option": {
            "required": False,
            "default": "",
            "description": "Optional option"
        }
    }
    
    async def run(self, **kwargs) -> dict:
        """Run test module"""
        return {
            "status": "success",
            "message": "Test module executed successfully",
            "options": self.current_options,
            "kwargs": kwargs
        }


class TestBaseModule:
    """Tests for BaseModule class"""
    
    def test_module_initialization(self):
        """Test module initialization"""
        module = TestModule()
        assert module.name == "test.module"
        assert module.description == "Test module"
        assert module.category == "test"
        assert module.subcategory == "test"
        assert "test_option" in module.current_options
    
    def test_set_option(self):
        """Test setting module option"""
        module = TestModule()
        result = module.set_option("test_option", "new_value")
        assert result is True
        assert module.current_options["test_option"] == "new_value"
    
    def test_set_invalid_option(self):
        """Test setting invalid option"""
        module = TestModule()
        result = module.set_option("invalid_option", "value")
        assert result is False
    
    def test_validate_options(self):
        """Test validating module options"""
        module = TestModule()
        # Required option is set to default value
        assert module.validate_options() is True
        
        # Remove required option
        module.current_options.pop("test_option")
        assert module.validate_options() is False
        
        # Set required option
        module.set_option("test_option", "value")
        assert module.validate_options() is True


class TestModuleRegistry:
    """Tests for ModuleRegistry class"""
    
    def test_register_module(self):
        """Test registering a module"""
        registry = ModuleRegistry()
        result = registry.register_module(TestModule)
        assert result is True
        assert "test.module" in registry.modules
    
    def test_register_duplicate_module(self):
        """Test registering a duplicate module"""
        registry = ModuleRegistry()
        registry.register_module(TestModule)
        result = registry.register_module(TestModule)
        assert result is False
    
    def test_get_module(self):
        """Test getting a registered module"""
        registry = ModuleRegistry()
        registry.register_module(TestModule)
        module_class = registry.get_module("test.module")
        assert module_class == TestModule
    
    def test_get_modules_by_category(self):
        """Test getting modules by category"""
        registry = ModuleRegistry()
        registry.register_module(TestModule)
        modules = registry.get_modules(category="test")
        assert "test.module" in modules
    
    def test_get_modules_by_subcategory(self):
        """Test getting modules by subcategory"""
        registry = ModuleRegistry()
        registry.register_module(TestModule)
        modules = registry.get_modules(category="test", subcategory="test")
        assert "test.module" in modules


class TestModuleRunner:
    """Tests for ModuleRunner class"""
    
    def test_run_sync(self):
        """Test running module synchronously"""
        runner = ModuleRunner()
        result = runner.run_module(TestModule, sync=True, test_option="test_value")
        assert result["status"] == "success"
        assert result["result"]["status"] == "success"
    
    def test_run_async(self):
        """Test running module asynchronously"""
        runner = ModuleRunner()
        result = runner.run_module(TestModule, sync=False, test_option="test_value")
        assert result["status"] == "running"
        assert "task_id" in result
    
    def test_invalid_options(self):
        """Test running module with invalid options"""
        runner = ModuleRunner()
        # Create module instance manually to test validation failure
        module = TestModule()
        # Remove the required option to trigger validation failure
        del module.current_options["test_option"]
        # Run the module directly with the invalid instance
        result = runner.run_sync(module)
        assert result["status"] == "error"
        assert "Invalid module options" in result["error"]
