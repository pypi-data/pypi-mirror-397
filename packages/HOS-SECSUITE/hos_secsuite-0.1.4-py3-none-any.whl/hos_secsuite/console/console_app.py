"""HOS SecSuite Console Application"""

import cmd
import sys
from typing import Dict, Any

from hos_secsuite import initialize, registry, runner
from hos_secsuite.console.ascii_logo import print_logo, ASCIITypes
from hos_secsuite.console.command_parser import CommandParser, Command


class HOSConsole(cmd.Cmd):
    """HOS SecSuite Interactive Console"""
    
    def __init__(self):
        super().__init__()
        self.prompt = "HOS > "
        self.intro = "Welcome to HOS SecSuite Console"
        self.current_module = None
        self.module_instance = None
        
        # Initialize framework
        initialize()
        
        # Command parser
        self.cmd_parser = CommandParser()
        
        # Register commands
        self._register_commands()
        
        # Show logo
        print_logo(ASCIITypes.STATIC)
    
    def _register_commands(self):
        """Register console commands"""
        commands = [
            Command(
                name="help",
                description="Show help information",
                handler=self.do_help,
                aliases=["?"]
            ),
            Command(
                name="modules",
                description="List available modules",
                handler=self.do_modules,
                aliases=["list"]
            ),
            Command(
                name="use",
                description="Use a module",
                handler=self.do_use
            ),
            Command(
                name="run",
                description="Run current module",
                handler=self.do_run
            ),
            Command(
                name="back",
                description="Return to main menu",
                handler=self.do_back,
                aliases=["exit_module"]
            ),
            Command(
                name="exit",
                description="Exit console",
                handler=self.do_exit,
                aliases=["quit", "q"]
            ),
            Command(
                name="search",
                description="Search for modules",
                handler=self.do_search
            ),
            Command(
                name="set",
                description="Set module option",
                handler=self.do_set
            ),
            Command(
                name="show",
                description="Show module options",
                handler=self.do_show
            ),
            Command(
                name="save",
                description="Save session",
                handler=self.do_save
            ),
            Command(
                name="load",
                description="Load session/script",
                handler=self.do_load
            )
        ]
        
        for command in commands:
            self.cmd_parser.register_command(command)
    
    def do_help(self, arg):
        """Show help information
        
        Usage: help [command]
        """
        if not arg:
            # Show all commands
            print("Available commands:")
            for cmd_name in sorted(self.cmd_parser.get_commands()):
                cmd = self.cmd_parser.commands[cmd_name]
                print(f"  {cmd_name:12} - {cmd.description}")
        else:
            # Show specific command help
            cmd = self.cmd_parser.get_command(arg)
            if cmd:
                print(f"{cmd.name}: {cmd.description}")
            else:
                print(f"Command '{arg}' not found")
    
    def do_modules(self, arg):
        """List available modules
        
        Usage: modules [category] [subcategory]
        """
        args = arg.split()
        category = args[0] if len(args) > 0 else None
        subcategory = args[1] if len(args) > 1 else None
        
        modules = registry.get_modules(category, subcategory)
        
        if not modules:
            print("No modules found")
            return
        
        print("Available modules:")
        for module_name in sorted(modules):
            module_class = registry.get_module(module_name)
            print(f"  {module_name:30} - {module_class.description}")
    
    def do_use(self, arg):
        """Use a module
        
        Usage: use <module_name>
        """
        if not arg:
            print("Please specify a module name")
            return
        
        try:
            module_class = registry.get_module(arg)
            self.current_module = arg
            self.module_instance = module_class()
            self.prompt = f"HOS({arg}) > "
            self.cmd_parser.current_module = arg
            print(f"Using module: {arg}")
        except KeyError:
            print(f"Module '{arg}' not found")
    
    def do_run(self, arg):
        """Run current module
        
        Usage: run [--async] [key=value ...]
        """
        if not self.current_module:
            print("No module selected. Use 'use <module>' first")
            return
        
        parsed = self.cmd_parser.parse(f"run {arg}")
        kwargs = parsed["kwargs"]
        
        # Check for async flag
        is_async = kwargs.pop("async", False)
        
        # Run the module
        result = runner.run_module(
            self.module_instance.__class__,
            sync=not is_async,
            **kwargs
        )
        
        # Print result
        if isinstance(result, dict):
            if result["status"] == "success":
                print(f"Module executed successfully")
                print(f"Result: {result['result']}")
            elif result["status"] == "running":
                print(f"Module started asynchronously")
                print(f"Task ID: {result['task_id']}")
            else:
                print(f"Module execution failed")
                print(f"Error: {result['error']}")
        else:
            print(f"Module result: {result}")
    
    def do_back(self, arg):
        """Return to main menu
        
        Usage: back
        """
        self.current_module = None
        self.module_instance = None
        self.prompt = "HOS > "
        self.cmd_parser.current_module = None
        print("Returned to main menu")
    
    def do_exit(self, arg):
        """Exit console
        
        Usage: exit
        """
        print("Exiting HOS SecSuite Console...")
        sys.exit(0)
    
    def do_search(self, arg):
        """Search for modules
        
        Usage: search <keyword>
        """
        if not arg:
            print("Please specify a search keyword")
            return
        
        keyword = arg.lower()
        found_modules = []
        
        for module_name, module_class in registry.modules.items():
            if keyword in module_name.lower() or keyword in module_class.description.lower():
                found_modules.append((module_name, module_class))
        
        if found_modules:
            print(f"Found {len(found_modules)} modules matching '{arg}':")
            for module_name, module_class in found_modules:
                print(f"  {module_name:30} - {module_class.description}")
        else:
            print(f"No modules found matching '{arg}'")
    
    def do_set(self, arg):
        """Set module option
        
        Usage: set <option> <value>
        """
        if not self.current_module:
            print("No module selected")
            return
        
        args = arg.split()
        if len(args) < 2:
            print("Usage: set <option> <value>")
            return
        
        option = args[0]
        value = " ".join(args[1:])
        
        if self.module_instance.set_option(option, value):
            print(f"Set {option} to {value}")
        else:
            print(f"Invalid option '{option}'")
    
    def do_show(self, arg):
        """Show module options
        
        Usage: show options
        """
        if not self.current_module:
            print("No module selected")
            return
        
        args = arg.split()
        if not args or args[0] != "options":
            print("Usage: show options")
            return
        
        print(f"Options for module {self.current_module}:")
        for opt_name, opt_value in self.module_instance.get_options().items():
            print(f"  {opt_name:20} = {opt_value}")
    
    def do_save(self, arg):
        """Save session
        
        Usage: save <session_file>
        """
        print("Session save functionality not implemented yet")
    
    def do_load(self, arg):
        """Load session/script
        
        Usage: load <file_path>
        """
        print("Session load functionality not implemented yet")
    
    def default(self, line):
        """Handle unknown commands
        
        Args:
            line: Input line
        """
        print(f"Unknown command: {line}")
        print("Type 'help' for available commands")
    
    def cmdloop(self, intro=None):
        """Command loop with improved handling
        
        Args:
            intro: Intro message
        """
        if intro:
            print(intro)
        
        while True:
            try:
                line = input(self.prompt)
                if line.strip():
                    self.onecmd(line)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nExiting HOS SecSuite Console...")
                break


def main():
    """Main entry point for console application"""
    console = HOSConsole()
    console.cmdloop()


if __name__ == "__main__":
    main()
