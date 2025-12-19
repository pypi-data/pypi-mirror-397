"""Module Runner for HOS SecSuite"""

import asyncio
import threading
from typing import Dict, Any, Optional, List
from hos_secsuite.core.base_module import BaseModule


class ModuleRunner:
    """Module runner to execute modules"""
    
    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_lock = threading.Lock()
    
    async def run_async(self, module_instance: BaseModule, **kwargs) -> Dict[str, Any]:
        """Run a module asynchronously
        
        Args:
            module_instance: Module instance to run
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Module execution result
        """
        try:
            result = await module_instance.run(**kwargs)
            return {
                "status": "success",
                "module": module_instance.name,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "module": module_instance.name,
                "error": str(e)
            }
    
    def run_sync(self, module_instance: BaseModule, **kwargs) -> Dict[str, Any]:
        """Run a module synchronously
        
        Args:
            module_instance: Module instance to run
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Module execution result
        """
        # Validate options before running
        if not module_instance.validate_options():
            return {
                "status": "error",
                "module": module_instance.name,
                "error": "Invalid module options"
            }
        
        # Use asyncio.run() for synchronous execution - recommended in modern Python
        return asyncio.run(self.run_async(module_instance, **kwargs))
    
    def run_module(self, module_class, sync: bool = True, **kwargs) -> Dict[str, Any]:
        """Run a module by class
        
        Args:
            module_class: Module class to run
            sync: Whether to run synchronously
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Module execution result
        """
        module_instance = module_class()
        
        # Set options from kwargs
        for key, value in kwargs.items():
            module_instance.set_option(key, value)
        
        # Validate options
        if not module_instance.validate_options():
            return {
                "status": "error",
                "module": module_class.name,
                "error": "Invalid module options"
            }
        
        if sync:
            return self.run_sync(module_instance, **kwargs)
        else:
            # For async execution, we need to handle event loop creation
            try:
                # Try to get existing loop
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            task = loop.create_task(self.run_async(module_instance, **kwargs))
            
            # Store task for tracking
            with self.task_lock:
                self.running_tasks[str(id(task))] = task
            
            return {
                "status": "running",
                "module": module_class.name,
                "task_id": str(id(task))
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a running task
        
        Args:
            task_id: Task ID to check
            
        Returns:
            Dict[str, Any]: Task status
        """
        with self.task_lock:
            if task_id not in self.running_tasks:
                return {
                    "status": "error",
                    "error": "Task not found"
                }
            
            task = self.running_tasks[task_id]
            
            if task.done():
                # Remove from running tasks
                del self.running_tasks[task_id]
                
                try:
                    result = task.result()
                    return result
                except Exception as e:
                    return {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                return {
                    "status": "running"
                }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        with self.task_lock:
            if task_id not in self.running_tasks:
                return False
            
            task = self.running_tasks[task_id]
            task.cancel()
            del self.running_tasks[task_id]
            return True
    
    def get_running_tasks(self) -> List[str]:
        """Get list of running task IDs
        
        Returns:
            List[str]: List of running task IDs
        """
        with self.task_lock:
            return list(self.running_tasks.keys())
