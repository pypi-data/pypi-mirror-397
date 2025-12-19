"""Command parser for HOS SecSuite console"""

import re
from typing import List, Dict, Callable


class Command:
    """Command definition"""
    
    def __init__(self, name: str, description: str, handler: Callable, aliases: List[str] = None):
        self.name = name
        self.description = description
        self.handler = handler
        self.aliases = aliases or []


class CommandParser:
    """Command parser for console input"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.current_module = None
        
    def register_command(self, command: Command):
        """Register a command
        
        Args:
            command: Command object
        """
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
    
    def parse(self, input_str: str) -> Dict:
        """Parse input string into command and arguments
        
        Args:
            input_str: Input string from console
            
        Returns:
            Dict: Parsed command info
        """
        # Remove leading/trailing whitespace
        input_str = input_str.strip()
        
        if not input_str:
            return {
                "command": None,
                "args": [],
                "kwargs": {}
            }
        
        # Split into tokens, preserving quoted strings
        # Use a safer approach to avoid quote escaping issues
        tokens = []
        current_token = ""
        in_quotes = None
        
        for char in input_str:
            if char in '"' and in_quotes is None:
                in_quotes = '"'
                current_token += char
            elif char == in_quotes:
                current_token += char
                tokens.append(current_token)
                current_token = ""
                in_quotes = None
            elif in_quotes is not None:
                current_token += char
            elif char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        if not tokens:
            return {
                "command": None,
                "args": [],
                "kwargs": {}
            }
        
        # First token is the command name
        command_name = tokens[0]
        remaining_tokens = tokens[1:]
        
        args = []
        kwargs = {}
        
        i = 0
        while i < len(remaining_tokens):
            token = remaining_tokens[i]
            
            # Check for kwargs (--key value or --flag)
            if token.startswith("--"):
                key = token[2:]
                
                # Check if next token exists and is not another flag
                if i + 1 < len(remaining_tokens) and not remaining_tokens[i + 1].startswith("--"):
                    value = remaining_tokens[i + 1]
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    kwargs[key] = value
                    i += 2
                else:
                    # Flag with no value (boolean)
                    kwargs[key] = True
                    i += 1
            else:
                # Normal argument
                # Remove quotes if present
                if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                    token = token[1:-1]
                args.append(token)
                i += 1
        
        return {
            "command": command_name,
            "args": args,
            "kwargs": kwargs
        }
    
    def get_command(self, name: str) -> Command:
        """Get a command by name
        
        Args:
            name: Command name or alias
            
        Returns:
            Command: Command object or None if not found
        """
        return self.commands.get(name)
    
    def get_commands(self) -> List[str]:
        """Get all command names
        
        Returns:
            List[str]: List of command names
        """
        # Return unique command names (excluding aliases)
        unique_commands = set()
        for cmd in self.commands.values():
            unique_commands.add(cmd.name)
        return list(unique_commands)
    
    def get_prompt(self) -> str:
        """Get current console prompt
        
        Returns:
            str: Console prompt
        """
        if self.current_module:
            return f"\033[32mHOS({self.current_module}) > \033[0m"
        else:
            return f"\033[32mHOS > \033[0m"
