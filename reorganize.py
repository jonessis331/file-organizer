#!/usr/bin/env python3
"""
Reorganize the file-organizer project structure
"""

import os
import shutil
from pathlib import Path
import re

def create_directories():
    """Create the new directory structure"""
    directories = [
        "backend",
        "backend/api",
        "backend/core",
        "backend/config",
        "backend/utils",
        "frontend/src",
        "frontend/public",
        "scripts",
        "tests/test_data",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory.startswith("backend") or directory == "tests":
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()

def move_files():
    """Move files to their new locations"""
    file_moves = {
        # Backend core modules
        "scanner.py": "backend/core/scanner.py",
        "organize.py": "backend/core/organizer.py",
        "backup.py": "backend/core/backup.py",
        "generate_prompt.py": "backend/core/prompt_generator.py",
        
        # API files
        "api.py": "backend/api/main.py",
        
        # Config files
        "config.py": "backend/config/settings.py",
        
        # Utils
        "cli.py": "backend/utils/cli.py",
        "main.py": "backend/utils/main_cli.py",  # Keep the CLI version
        
        # Scripts
        "setup.py": "scripts/setup.py",
        "create_test_folder.py": "scripts/create_test_folder.py",
        "run_api.sh": "scripts/run_api.sh",
        
        # Tests
        "test_api.py": "tests/test_api.py",
        "test_components.py": "tests/test_components.py",
    }
    
    for old_path, new_path in file_moves.items():
        if Path(old_path).exists():
            print(f"Moving {old_path} -> {new_path}")
            shutil.move(old_path, new_path)

def update_imports_in_file(file_path, import_map):
    """Update imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Update imports
    for old_import, new_import in import_map.items():
        # Handle different import styles
        patterns = [
            (rf'from {old_import} import', f'from {new_import} import'),
            (rf'import {old_import}', f'import {new_import}'),
        ]
        
        for old_pattern, new_pattern in patterns:
            content = re.sub(old_pattern, new_pattern, content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated imports in {file_path}")

def update_all_imports():
    """Update all import statements"""
    import_map = {
        # Core modules
        'scanner': 'backend.core.scanner',
        'organize': 'backend.core.organizer',
        'backup': 'backend.core.backup',
        'generate_prompt': 'backend.core.prompt_generator',
        
        # Config
        'config': 'backend.config.settings',
        
        # Utils
        'cli': 'backend.utils.cli',
    }
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip venv and other directories
        if any(skip in root for skip in ['venv', '__pycache__', '.git', 'node_modules']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Update imports in each file
    for file_path in python_files:
        update_imports_in_file(file_path, import_map)

def create_new_files():
    """Create new configuration files"""
    
    # Create pyproject.toml
    pyproject_content = '''[tool.poetry]
    name = "file-organizer"
    version = "1.0.0"
    description = "AI-powered file organization desktop app"
    authors = ["Your Name <your.email@example.com>"]

    [tool.poetry.dependencies]
    python = "^3.8"
    fastapi = "^0.104.0"
    uvicorn = {extras = ["standard"], version = "^0.24.0"}
    pydantic = "^2.0.0"
    tqdm = "^4.65.0"
    python-docx = "^0.8.11"
    PyMuPDF = "^1.23.0"

    [tool.poetry.dev-dependencies]
    pytest = "^7.4.0"
    black = "^23.0.0"
    flake8 = "^6.0.0"
    mypy = "^1.0.0"

    [build-system]
    requires = ["poetry-core>=1.0.0"]
    build-backend = "poetry.core.masonry.api"

    [tool.black]
    line-length = 100
    target-version = ['py38']

    [tool.mypy]
    python_version = "3.8"
    warn_return_any = true
    warn_unused_configs = true
    '''
    
    with open('pyproject.toml', 'w') as f:
        f.write(pyproject_content)
    
    # Create updated .gitignore
    gitignore_content = '''# Python
    __pycache__/
    *.py[cod]
    *$py.class
    *.so
    .Python
    venv/
    env/
    ENV/
    .venv

    # IDE
    .vscode/
    .idea/
    *.swp
    *.swo
    .DS_Store

    # Project specific
    data/
    logs/
    *.log
    .env
    test_folder/

    # Distribution
    dist/
    build/
    *.egg-info/

    # Testing
    .pytest_cache/
    .coverage
    htmlcov/
    .tox/
    .mypy_cache/

    # Node (for frontend)
    node_modules/
    npm-debug.log*
    yarn-debug.log*
    yarn-error.log*
    '''
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    # Create backend/__init__.py with version info
    backend_init = '''"""
    File Organizer Backend
    """

    __version__ = "1.0.0"
    '''
    
    with open('backend/__init__.py', 'w') as f:
        f.write(backend_init)
    
    # Create backend/api/__init__.py
    api_init = '''"""
    FastAPI application and routes
    """

    from .main import app

    __all__ = ["app"]
    '''
    
    with open('backend/api/__init__.py', 'w') as f:
        f.write(api_init)

def create_run_scripts():
    """Create new run scripts with updated paths"""
    
    # Update run_api.sh
    run_api_content = '''#!/bin/bash

    # File Organizer API Startup Script

    echo "🚀 Starting File Organizer API..."

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt

    # Create necessary directories
    echo "📁 Creating directories..."
    mkdir -p data logs

    # Start the API
    echo "🚀 Starting FastAPI server..."
    echo "=================================================="
    echo "API will be available at: http://localhost:8765"
    echo "API Documentation: http://localhost:8765/docs"
    echo "=================================================="
    echo ""

    # Run the API with the new path
    cd backend && python -m api.main
    '''
    
    with open('scripts/run_api.sh', 'w') as f:
        f.write(run_api_content)
    os.chmod('scripts/run_api.sh', 0o755)
    
    # Create run_dev.sh for development
    run_dev_content = '''#!/bin/bash

    # Development mode with auto-reload

    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

    echo "🔄 Starting API in development mode with auto-reload..."
    cd backend && uvicorn api.main:app --reload --host 127.0.0.1 --port 8765
    '''
        
    with open('scripts/run_dev.sh', 'w') as f:
        f.write(run_dev_content)
    os.chmod('scripts/run_dev.sh', 0o755)

def main():
    """Run the reorganization"""
    print("🔧 Reorganizing File Organizer project...")
    
    # Confirm with user
    response = input("\n⚠️  This will reorganize your project structure. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Reorganization cancelled")
        return
    
    print("\n📁 Creating new directory structure...")
    create_directories()
    
    print("\n📦 Moving files...")
    move_files()
    
    print("\n📝 Creating new configuration files...")
    create_new_files()
    
    print("\n🔧 Creating run scripts...")
    create_run_scripts()
    
    print("\n🔄 Updating imports...")
    update_all_imports()
    
    print("\n✨ Reorganization complete!")
    print("\nNext steps:")
    print("1. Update any remaining imports manually if needed")
    print("2. Test the API: ./scripts/run_api.sh")
    print("3. Run tests: pytest tests/")
    print("\n📁 New structure:")
    print("   backend/     - All Python code")
    print("   frontend/    - Future Electron app")
    print("   scripts/     - Utility scripts")
    print("   tests/       - All tests")

if __name__ == "__main__":
    main()