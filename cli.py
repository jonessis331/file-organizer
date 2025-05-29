"""
Command Line Interface utilities for the File Organizer
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @classmethod
    def disable(cls):
        """Disable colors (for non-terminal output)"""
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.WARNING = ''
        cls.FAIL = ''
        cls.ENDC = ''
        cls.BOLD = ''
        cls.UNDERLINE = ''

class CLI:
    """Command line interface helper"""
    
    def __init__(self, use_colors=True):
        if not use_colors or not sys.stdout.isatty():
            Colors.disable()
            
    def header(self, text):
        """Print a header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
        print("=" * len(text))
        
    def success(self, text):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
        
    def error(self, text):
        """Print error message"""
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")
        
    def warning(self, text):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")
        
    def info(self, text):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")
        
    def confirm(self, prompt, default=False):
        """Ask for confirmation"""
        default_text = "Y/n" if default else "y/N"
        
        while True:
            response = input(f"{Colors.WARNING}{prompt} [{default_text}]: {Colors.ENDC}").strip().lower()
            
            if not response:
                return default
                
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                self.error("Please answer 'yes' or 'no'")
    
    def choose_option(self, prompt, options, default=None):
        """Present a menu and get user choice"""
        print(f"\n{Colors.CYAN}{prompt}{Colors.ENDC}")
        
        for i, option in enumerate(options, 1):
            prefix = "[*]" if default and option == default else f"[{i}]"
            print(f"  {prefix} {option}")
            
        while True:
            choice = input(f"\n{Colors.WARNING}Enter choice (1-{len(options)}): {Colors.ENDC}").strip()
            
            if not choice and default:
                return default
                
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                else:
                    self.error("Invalid choice. Please try again.")
            except ValueError:
                self.error("Please enter a number.")
    
    def input_path(self, prompt="Enter path"):
        """Get a valid path from user"""
        while True:
            path = input(f"{Colors.WARNING}{prompt}: {Colors.ENDC}").strip()
            
            if not path:
                self.error("Path cannot be empty")
                continue
                
            # Expand user home directory
            path = os.path.expanduser(path)
            path = Path(path).resolve()
            
            if not path.exists():
                self.error(f"Path does not exist: {path}")
                if not self.confirm("Would you like to create it?"):
                    continue
                try:
                    os.makedirs(path, exist_ok=True)
                    self.success(f"Created directory: {path}")
                except Exception as e:
                    self.error(f"Failed to create directory: {e}")
                    continue
                    
            return str(path)
    
    def show_statistics(self, stats):
        """Display statistics in a nice format"""
        self.header("📊 Statistics")
        
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\n{Colors.BOLD}{key}:{Colors.ENDC}")
                for sub_key, sub_value in value.items():
                    print(f"  • {sub_key}: {sub_value}")
            else:
                print(f"• {key}: {value}")
    
    def progress_message(self, message, current=None, total=None):
        """Show a progress message"""
        if current is not None and total is not None:
            percentage = (current / total) * 100 if total > 0 else 0
            print(f"\r{Colors.CYAN}⏳ {message} [{current}/{total}] {percentage:.1f}%{Colors.ENDC}", 
                  end='', flush=True)
        else:
            print(f"{Colors.CYAN}⏳ {message}...{Colors.ENDC}")
    
    def clear_line(self):
        """Clear the current line"""
        print('\r' + ' ' * 80 + '\r', end='', flush=True)
        
    def print_tree(self, items, indent=0):
        """Print items in a tree structure"""
        for item in items:
            print('  ' * indent + '├── ' + str(item))
            
    def format_size(self, size_bytes):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def format_timestamp(self, timestamp):
        """Format timestamp to readable date"""
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return str(timestamp)
    
    def print_banner(self):
        """Print application banner"""
        banner = """
        ╔═══════════════════════════════════════════════════╗
        ║          🗂️  INTELLIGENT FILE ORGANIZER 🗂️         ║
        ║                                                   ║
        ║  Declutter and organize your files using AI       ║
        ║  Built with KonMari principles                    ║
        ╚═══════════════════════════════════════════════════╝
        """
        print(f"{Colors.HEADER}{banner}{Colors.ENDC}")

# Utility functions for quick access
def confirm(prompt, default=False):
    """Quick confirm function"""
    cli = CLI()
    return cli.confirm(prompt, default)

def success(message):
    """Quick success message"""
    cli = CLI()
    cli.success(message)

def error(message):
    """Quick error message"""
    cli = CLI()
    cli.error(message)

def warning(message):
    """Quick warning message"""
    cli = CLI()
    cli.warning(message)

def info(message):
    """Quick info message"""
    cli = CLI()
    cli.info(message)