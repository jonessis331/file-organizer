#!/usr/bin/env python3
"""
Create a test folder structure for testing the file organizer
"""

import os
from pathlib import Path
import random
import datetime

def create_test_folder():
    """Create a test folder with various file types"""
    test_dir = Path("test_folder")
    
    # Remove existing test folder if it exists
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    print("🏗️  Creating test folder structure...")
    
    # Create test files
    test_files = {
        # Documents
        "test_folder/resume_2024.txt": "John Doe\nSoftware Engineer\nExperience: 5 years",
        "test_folder/cover_letter.txt": "Dear Hiring Manager,\nI am applying for...",
        "test_folder/invoice_jan2024.txt": "Invoice #1234\nAmount: $500",
        "test_folder/meeting_notes.txt": "Meeting notes from Jan 15, 2024",
        
        # Code files
        "test_folder/script.py": "import os\nprint('Hello World')",
        "test_folder/index.html": "<html><body><h1>Test</h1></body></html>",
        "test_folder/style.css": "body { margin: 0; padding: 0; }",
        
        # Personal files
        "test_folder/vacation_plans.txt": "Trip to Hawaii - June 2024",
        "test_folder/shopping_list.txt": "Milk, Bread, Eggs",
        
        # Nested folders
        "test_folder/downloads/setup.txt": "[This would be a setup file]",
        "test_folder/downloads/manual.txt": "User Manual v1.0",
        "test_folder/old_files/report_2020.txt": "Annual Report 2020",
        "test_folder/old_files/backup_2019.txt": "Backup data from 2019",
        
        # Project folder (should be preserved)
        "test_folder/my_project/README.md": "# My Project\nThis is a test project",
        "test_folder/my_project/main.py": "def main():\n    pass",
        "test_folder/my_project/requirements.txt": "fastapi\nuvicorn",
        "test_folder/my_project/.gitignore": "*.pyc\n__pycache__",
        
        # Random files
        "test_folder/random_note.txt": "Remember to call mom",
        "test_folder/todo_list.txt": "1. Finish project\n2. Clean room",
    }
    
    # Create files
    created_count = 0
    for file_path, content in test_files.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        created_count += 1
        print(f"✅ Created: {file_path}")
    
    # Create some empty files
    for i in range(5):
        empty_file = test_dir / f"empty_file_{i}.txt"
        empty_file.touch()
        created_count += 1
    
    print(f"\n✨ Created test folder with {created_count} files")
    print(f"📁 Test folder location: {test_dir.absolute()}")
    
    return str(test_dir.absolute())

if __name__ == "__main__":
    create_test_folder()