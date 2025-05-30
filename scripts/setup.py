#!/usr/bin/env python3
"""
Setup script for File Organizer
Creates necessary directories and validates environment
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directory structure"""
    directories = [
        "data",
        "data/backup_archives",
        "logs",
        "tests"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = {
        "tqdm": "Progress bars",
        "docx": "Word document support",
        "fitz": "PDF support (PyMuPDF)",
    }
    
    optional_packages = {
        "openai": "OpenAI API support",
        "colorama": "Colored terminal output",
        "magic": "File type detection"
    }
    
    missing_required = []
    missing_optional = []
    
    print("\n🔍 Checking dependencies...")
    
    # Check required packages
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} - {description} (REQUIRED)")
    
    # Check optional packages
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} - {description} (optional)")
    
    return missing_required, missing_optional

def install_dependencies(packages):
    """Install missing packages"""
    if not packages:
        return True
        
    print(f"\n📦 Installing {len(packages)} packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print(f"✅ OpenAI API key configured (starts with: {api_key[:10]}...)")
        return True
    else:
        print("⚠️  OpenAI API key not found (optional - needed for automatic mode)")
        print("   To set: export OPENAI_API_KEY='your-key-here'")
        return False

def create_test_structure():
    """Create a test folder structure for testing"""
    test_dir = Path("test_folder")
    
    if test_dir.exists():
        print(f"\n⚠️  Test folder already exists: {test_dir}")
        return
    
    print(f"\n🏗️  Creating test folder structure...")
    
    # Create test structure
    test_files = {
        "test_folder/resume_2024.pdf": "Resume content",
        "test_folder/invoice_january.pdf": "Invoice content",
        "test_folder/vacation_photo.jpg": "",
        "test_folder/project_notes.txt": "Project planning notes",
        "test_folder/downloads/setup.exe": "",
        "test_folder/downloads/manual.pdf": "User manual",
        "test_folder/code/script.py": "import os\nprint('Hello')",
        "test_folder/code/index.html": "<html><body>Test</body></html>",
        "test_folder/old_files/report_2020.doc": "Old report",
        "test_folder/old_files/backup_2019.zip": "",
    }
    
    for file_path, content in test_files.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if content:
            path.write_text(content)
        else:
            path.touch()
    
    print(f"✅ Created test folder with {len(test_files)} files")
    print(f"   Test with: python main.py test_folder")

def main():
    """Run setup process"""
    print("🚀 File Organizer Setup")
    print("=" * 50)
    
    # 1. Create directories
    print("\n📁 Creating directory structure...")
    create_directories()
    
    # 2. Check dependencies
    missing_required, missing_optional = check_dependencies()
    
    if missing_required:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_required)}")
        response = input("\nInstall missing dependencies? [Y/n]: ").strip().lower()
        
        if response != 'n':
            success = install_dependencies(missing_required)
            if not success:
                print("\n❌ Setup failed. Please install dependencies manually:")
                print("   pip install -r requirements.txt")
                sys.exit(1)
    
    # 3. Check API key
    print("\n🔑 Checking API configuration...")
    check_api_key()
    
    # 4. Create test structure
    response = input("\n📁 Create test folder for testing? [y/N]: ").strip().lower()
    if response == 'y':
        create_test_structure()
    
    # 5. Final message
    print("\n" + "=" * 50)
    print("✨ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python main.py /path/to/folder")
    print("2. Or test with: python main.py test_folder")
    print("\nFor help: python main.py --help")

if __name__ == "__main__":
    main()