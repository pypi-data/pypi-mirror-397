"""HOS SecSuite - Modular Network Security Toolkit"""

__version__ = "0.1.4"
__author__ = "HOS"
__email__ = "security@example.com"
__license__ = "Apache-2.0"

from hos_secsuite.core.registry import ModuleRegistry
from hos_secsuite.core.runner import ModuleRunner

# 全局模块注册表
registry = ModuleRegistry()
runner = ModuleRunner()

# 初始化模块注册
def initialize():
    """Initialize the HOS SecSuite framework"""
    registry.scan_modules()
