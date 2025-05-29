#!/usr/bin/env python3
"""
Test script to verify each component of the File Organizer
Run this to test individual modules
"""

import os
import sys
import json
from pathlib import Path
import tempfile
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_scanner():
    """Test the scanner module"""
    print("\n🔍 Testing Scanner Module...")
    
    try:
        from scanner import scan_directory, analyze_folder_structure
        
        # Create a temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "test.txt").write_text("Hello World")
            (Path(temp_dir) / "test.pdf").touch()
            (Path(temp_dir) / "subdir").mkdir()
            (Path(temp_dir) / "subdir" / "test2.py").write_text("print('test')")
            
            # Test scanning
            files = scan_directory(temp_dir)
            print(f"✅ Scanned {len(files)} files")
            
            # Test analysis
            analysis = analyze_folder_structure(temp_dir)
            print(f"✅ Analysis complete: {analysis['total_files']} total files")
            
            return True
            
    except Exception as e:
        print(f"❌ Scanner test failed: {e}")
        return False

def test_prompt_generator():
    """Test the prompt generator module"""
    print("\n📝 Testing Prompt Generator...")
    
    try:
        from generate_prompt import generate_konmari_prompt, save_prompt
        
        # Create test scan results
        test_results = {
            "scan_date": "2024-01-01",
            "root_path": "/test",
            "analysis": {
                "total_files": 5,
                "organized_folders": [],
                "file_types": {".txt": 3, ".pdf": 2}
            },
            "files": [
                {
                    "name": "test.txt",
                    "relative_path": "test.txt",
                    "extension": ".txt",
                    "size_kb": 1.5,
                    "created": "2024-01-01",
                    "modified": "2024-01-01",
                    "content_snippet": "Test content"
                }
            ]
        }
        
        # Save test results
        os.makedirs("data", exist_ok=True)
        with open("data/scan_results.json", "w") as f:
            json.dump(test_results, f)
        
        # Generate prompt
        prompt = generate_konmari_prompt("/test", max_files=10)
        print(f"✅ Generated prompt: {len(prompt)} characters")
        
        # Save prompt
        save_prompt("Test prompt content")
        print("✅ Saved prompt to file")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt generator test failed: {e}")
        return False

def test_organizer():
    """Test the organizer module"""
    print("\n🚀 Testing Organizer Module...")
    
    try:
        from organize import validate_plan, perform_file_moves
        
        # Create test plan
        test_plan = {
            "folders": ["TestFolder"],
            "moves": [
                {
                    "file": "test.txt",
                    "relative_path": "test.txt",
                    "new_path": "TestFolder/test.txt",
                    "reason": "Test move"
                }
            ]
        }
        
        # Test validation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")
            
            # Validate plan
            issues = validate_plan(test_plan, temp_dir)
            print(f"✅ Plan validation: {len(issues)} issues")
            
            # Test dry run
            success = perform_file_moves(temp_dir, test_plan, dry_run=True)
            print(f"✅ Dry run completed: {success}")
            
        return True
        
    except Exception as e:
        print(f"❌ Organizer test failed: {e}")
        return False

def test_backup():
    """Test the backup module"""
    print("\n💾 Testing Backup Module...")
    
    try:
        from backup import create_backup_manifest, calculate_file_hash
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")
            
            # Test hash calculation
            file_hash = calculate_file_hash(test_file)
            print(f"✅ File hash calculated: {file_hash[:10]}...")
            
            # Test manifest creation
            test_plan = {
                "moves": [{
                    "file": "test.txt",
                    "relative_path": "test.txt",
                    "new_path": "folder/test.txt"
                }]
            }
            
            os.makedirs("data", exist_ok=True)
            manifest = create_backup_manifest(temp_dir, test_plan)
            print(f"✅ Backup manifest created: {len(manifest['original_state'])} files")
            
        return True
        
    except Exception as e:
        print(f"❌ Backup test failed: {e}")
        return False

def test_config():
    """Test the configuration module"""
    print("\n⚙️  Testing Configuration Module...")
    
    try:
        from config import Config
        
        # Test file categorization
        category = Config.get_file_category(".pdf")
        print(f"✅ File category for .pdf: {category}")
        
        # Test project detection
        is_project = Config.is_project_file("package.json")
        print(f"✅ Project file detection: {is_project}")
        
        # Test skip folder
        should_skip = Config.should_skip_folder(".git")
        print(f"✅ Skip folder detection: {should_skip}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_cli():
    """Test the CLI module"""
    print("\n🖥️  Testing CLI Module...")
    
    try:
        from cli import CLI, Colors
        
        cli = CLI()
        
        # Test output methods
        cli.success("Success message test")
        cli.error("Error message test")
        cli.warning("Warning message test")
        cli.info("Info message test")
        
        # Test formatting
        size = cli.format_size(1024 * 1024)
        print(f"✅ Size formatting: {size}")
        
        # Test tree printing
        print("✅ Tree structure:")
        cli.print_tree(["Item 1", "Item 2", "Item 3"])
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all component tests"""
    print("🧪 File Organizer Component Tests")
    print("=" * 50)
    
    tests = [
        ("Scanner", test_scanner),
        ("Prompt Generator", test_prompt_generator),
        ("Organizer", test_organizer),
        ("Backup", test_backup),
        ("Configuration", test_config),
        ("CLI", test_cli)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run setup: python setup.py")
        print("2. Test with: python main.py test_folder")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()