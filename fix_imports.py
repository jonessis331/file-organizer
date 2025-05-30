#!/usr/bin/env python3
"""
Quick import fixer for the reorganized project
Run this after reorganizing to fix all imports
"""

import os
import re
from pathlib import Path

# Import mappings
IMPORT_FIXES = {
    # API main file
    'backend/api/main.py': [
        ('from scanner import', 'from backend.core.scanner import'),
        ('from generate_prompt import', 'from backend.core.prompt_generator import'),
        ('from organize import', 'from backend.core.organizer import'),
        ('from backup import', 'from backend.core.backup import'),
        ('from config import', 'from backend.config.settings import'),
        ('import scanner', 'from backend.core import scanner'),
        ('import organize', 'from backend.core import organizer'),
        ('import backup', 'from backend.core import backup'),
        ('import config', 'from backend.config import settings as config'),
    ],
    
    # Core modules
    'backend/core/scanner.py': [
        ('from docx import', 'from docx import'),  # External lib, no change
        ('import fitz', 'import fitz'),  # External lib, no change
    ],
    
    'backend/core/organizer.py': [
        ('from scanner import', 'from .scanner import'),
        ('from backup import', 'from .backup import'),
        ('from organize import create_backup_manifest', 'from .backup import create_backup_manifest'),
    ],
    
    'backend/core/prompt_generator.py': [
        ('from scanner import', 'from .scanner import'),
    ],
    
    'backend/core/backup.py': [
        ('from organize import', 'from .organizer import'),
    ],
    
    # Utils
    'backend/utils/main_cli.py': [
        ('from scanner import', 'from backend.core.scanner import'),
        ('from generate_prompt import', 'from backend.core.prompt_generator import'),
        ('from organize import', 'from backend.core.organizer import'),
        ('from backup import', 'from backend.core.backup import'),
        ('from config import', 'from backend.config.settings import'),
        ('from cli import', 'from .cli import'),
    ],
    
    # Tests
    'tests/test_api.py': [
        # Tests will use absolute imports
        ('from scanner import', 'from backend.core.scanner import'),
        ('from generate_prompt import', 'from backend.core.prompt_generator import'),
        ('from organize import', 'from backend.core.organizer import'),
        ('from backup import', 'from backend.core.backup import'),
        ('from config import', 'from backend.config.settings import'),
        ('from cli import', 'from backend.utils.cli import'),
    ],
    
    'tests/test_components.py': [
        ('from scanner import', 'from backend.core.scanner import'),
        ('from generate_prompt import', 'from backend.core.prompt_generator import'),
        ('from organize import', 'from backend.core.organizer import'),
        ('from backup import', 'from backend.core.backup import'),
        ('from config import', 'from backend.config.settings import'),
        ('from cli import', 'from backend.utils.cli import'),
    ],
}

# Additional regex patterns for edge cases
REGEX_PATTERNS = [
    # Fix relative imports in moved files
    (r'sys\.path\.append\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)', 
     'sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))'),
]

def fix_file_imports(file_path, fixes):
    """Fix imports in a specific file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        
        # Apply specific fixes
        for old, new in fixes:
            content = content.replace(old, new)
        
        # Apply regex patterns
        for pattern, replacement in REGEX_PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Fixed imports in {file_path}")
            return True
        return False
    except FileNotFoundError:
        print(f"⚠️  File not found: {file_path}")
        return False

def add_path_setup_to_tests():
    """Add path setup to test files for easier imports"""
    test_path_setup = '''import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

'''
    
    for test_file in ['tests/test_api.py', 'tests/test_components.py']:
        if Path(test_file).exists():
            with open(test_file, 'r') as f:
                content = f.read()
            
            if 'sys.path.insert' not in content:
                with open(test_file, 'w') as f:
                    f.write(test_path_setup + content)
                print(f"✅ Added path setup to {test_file}")

def create_backend_config_init():
    """Create proper __init__.py for config module"""
    config_init = '''"""
Configuration module
"""

from .settings import Config, config

__all__ = ["Config", "config"]
'''
    
    init_path = Path('backend/config/__init__.py')
    if init_path.parent.exists():
        with open(init_path, 'w') as f:
            f.write(config_init)

def main():
    """Run all import fixes"""
    print("🔧 Fixing imports in reorganized project...")
    
    # Fix imports in each file
    fixed_count = 0
    for file_path, fixes in IMPORT_FIXES.items():
        if fix_file_imports(file_path, fixes):
            fixed_count += 1
    
    # Add path setup to tests
    add_path_setup_to_tests()
    
    # Create proper init files
    create_backend_config_init()
    
    print(f"\n✅ Fixed imports in {fixed_count} files")
    print("\n📝 Additional manual fixes may be needed for:")
    print("   - Circular imports")
    print("   - Dynamic imports")
    print("   - String-based imports")
    
    print("\n🧪 Test your setup:")
    print("   1. Run API: ./scripts/run_api.sh")
    print("   2. Run tests: pytest tests/")

if __name__ == "__main__":
    main()