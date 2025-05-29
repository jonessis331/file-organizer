#!/usr/bin/env python3
"""
File Organizer - Main Entry Point
Orchestrates the complete file organization workflow
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner import scan_directory, analyze_folder_structure
from generate_prompt import generate_and_send_prompt, generate_konmari_prompt, save_prompt
from organize import perform_file_moves, load_plan, cleanup_empty_folders
from backup import create_full_backup, revert_organization, list_backups
from config import Config
from cli import CLI

class FileOrganizer:
    """Main orchestrator for the file organization system"""
    
    def __init__(self):
        self.config = Config()
        self.cli = CLI()
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/backup_archives", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
    def run_full_workflow(self, target_path, auto_mode=False):
        """Run the complete organization workflow"""
        
        print(f"\n🗂️  File Organizer - Full Workflow")
        print(f"📁 Target: {target_path}")
        print("="*50)
        
        # Step 1: Analyze directory
        print("\n📊 Step 1: Analyzing directory structure...")
        analysis = analyze_folder_structure(target_path)
        print(f"✅ Found {analysis['total_files']} files")
        print(f"📁 Organized folders detected: {len(analysis['organized_folders'])}")
        
        # Step 2: Create safety backup
        if self.cli.confirm("\n💾 Create a safety backup before proceeding?"):
            print("\n📸 Creating safety backup...")
            backup_file = create_full_backup(target_path)
            print(f"✅ Backup saved to: {backup_file}")
        
        # Step 3: Scan files
        print("\n🔍 Step 2: Scanning files...")
        files = scan_directory(target_path, max_files=self.config.MAX_FILES_TO_SCAN)
        
        # Save scan results
        scan_results = {
            "scan_date": datetime.now().isoformat(),
            "root_path": str(target_path),
            "analysis": analysis,
            "files": files
        }
        
        with open("data/scan_results.json", "w") as f:
            json.dump(scan_results, f, indent=2)
        
        print(f"✅ Scanned {len(files)} files")
        
        # Step 4: Generate organization plan
        print("\n🤖 Step 3: Generating organization plan...")
        
        if auto_mode and self.config.OPENAI_API_KEY:
            # Auto mode with API
            plan = generate_and_send_prompt(target_path, self.config.OPENAI_API_KEY)
            if not plan:
                print("❌ Failed to generate plan automatically")
                return False
        else:
            # Manual mode
            prompt = generate_konmari_prompt(target_path)
            prompt_file = save_prompt(prompt)
            
            print(f"\n📝 Prompt saved to: {prompt_file}")
            print("\n" + "="*50)
            print("📋 Next steps:")
            print("1. Copy the prompt from data/gpt_prompt.txt")
            print("2. Paste it into ChatGPT or Claude")
            print("3. Copy the JSON response")
            print("4. Save it to data/plan.json")
            print("5. Run this script again with --execute flag")
            print("="*50)
            
            if not self.cli.confirm("\n✅ Have you saved the plan to data/plan.json?"):
                print("❌ Workflow paused. Run again after saving the plan.")
                return False
        
        # Step 5: Review plan
        print("\n📋 Step 4: Reviewing organization plan...")
        try:
            plan = load_plan()
            print(f"✅ Plan loaded: {len(plan.get('moves', []))} files to move")
            print(f"📁 New folders to create: {len(plan.get('folders', []))}")
            
            # Show sample moves
            print("\n📄 Sample moves:")
            for move in plan.get('moves', [])[:5]:
                print(f"  • {move['file']} → {move['new_path']}")
                print(f"    Reason: {move['reason']}")
            
            if len(plan.get('moves', [])) > 5:
                print(f"  ... and {len(plan.get('moves', [])) - 5} more moves")
                
        except Exception as e:
            print(f"❌ Error loading plan: {e}")
            return False
        
        # Step 6: Execute plan
        if self.cli.confirm("\n🚀 Execute the organization plan?"):
            # Dry run first
            if self.cli.confirm("📊 Perform a dry run first?"):
                print("\n🔍 Performing dry run...")
                perform_file_moves(target_path, plan, dry_run=True)
                
                if not self.cli.confirm("\n✅ Dry run complete. Proceed with actual organization?"):
                    print("❌ Organization cancelled")
                    return False
            
            # Actual execution
            print("\n🚀 Executing organization plan...")
            success = perform_file_moves(target_path, plan, dry_run=False)
            
            if success:
                # Cleanup empty folders
                cleanup_empty_folders(target_path)
                
                print("\n✨ Organization completed successfully!")
                print("💾 Backup manifest saved to: data/backup_manifest.json")
                print("🔄 To revert: python backup.py --revert")
                return True
            else:
                print("\n❌ Organization failed")
                return False
        else:
            print("❌ Organization cancelled")
            return False
    
    def run_scan_only(self, target_path):
        """Run only the scanning step"""
        print(f"\n🔍 Scanning directory: {target_path}")
        
        analysis = analyze_folder_structure(target_path)
        files = scan_directory(target_path)
        
        # Save results
        results = {
            "scan_date": datetime.now().isoformat(),
            "root_path": str(target_path),
            "analysis": analysis,
            "files": files
        }
        
        output_file = "data/scan_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"\n✅ Scan complete!")
        print(f"📊 Total files: {len(files)}")
        print(f"📁 Organized folders: {len(analysis['organized_folders'])}")
        print(f"💾 Results saved to: {output_file}")
        
        # Show file type distribution
        print("\n📈 File type distribution:")
        sorted_types = sorted(analysis['file_types'].items(), 
                            key=lambda x: x[1], 
                            reverse=True)[:10]
        for ext, count in sorted_types:
            print(f"  {ext or 'no-ext'}: {count} files")
            
    def run_prompt_only(self, target_path):
        """Generate prompt only"""
        print(f"\n📝 Generating prompt for: {target_path}")
        
        # Check if scan results exist
        if not Path("data/scan_results.json").exists():
            print("⚠️  No scan results found. Running scan first...")
            self.run_scan_only(target_path)
        
        prompt = generate_konmari_prompt(target_path)
        prompt_file = save_prompt(prompt)
        
        print(f"\n✅ Prompt generated!")
        print(f"📄 Saved to: {prompt_file}")
        print(f"📏 Length: {len(prompt)} characters")
        print("\n📋 Next steps:")
        print("1. Copy the prompt from data/gpt_prompt.txt")
        print("2. Paste into ChatGPT or Claude")
        print("3. Save the JSON response to data/plan.json")
        print("4. Run: python main.py <path> --execute")
        
    def run_execute_only(self, target_path):
        """Execute existing plan"""
        print(f"\n🚀 Executing plan for: {target_path}")
        
        try:
            plan = load_plan()
            print(f"✅ Plan loaded: {len(plan.get('moves', []))} moves")
            
            if self.cli.confirm("\n📊 Perform dry run first?"):
                perform_file_moves(target_path, plan, dry_run=True)
                
                if not self.cli.confirm("\n✅ Proceed with actual execution?"):
                    print("❌ Execution cancelled")
                    return
                    
            success = perform_file_moves(target_path, plan, dry_run=False)
            
            if success:
                cleanup_empty_folders(target_path)
                print("\n✨ Organization complete!")
                
        except FileNotFoundError:
            print("❌ No plan.json found. Generate a plan first.")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🗂️  Intelligent File Organizer - Declutter and organize your files using AI"
    )
    
    parser.add_argument("path", help="Path to organize")
    parser.add_argument("--scan", action="store_true", 
                       help="Only scan directory (step 1)")
    parser.add_argument("--prompt", action="store_true", 
                       help="Only generate prompt (step 2)")
    parser.add_argument("--execute", action="store_true", 
                       help="Execute existing plan (step 3)")
    parser.add_argument("--auto", action="store_true", 
                       help="Automatic mode using OpenAI API")
    parser.add_argument("--revert", action="store_true", 
                       help="Revert last organization")
    parser.add_argument("--backups", action="store_true", 
                       help="List available backups")
    
    args = parser.parse_args()
    
    # Validate path
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"❌ Path not found: {target_path}")
        sys.exit(1)
        
    if not target_path.is_dir():
        print(f"❌ Not a directory: {target_path}")
        sys.exit(1)
    
    # Initialize organizer
    organizer = FileOrganizer()
    
    # Handle commands
    if args.revert:
        try:
            revert_organization()
        except Exception as e:
            print(f"❌ Revert failed: {e}")
            
    elif args.backups:
        backups = list_backups()
        if backups:
            print("\n📦 Available backups:")
            for b in backups:
                print(f"\n  Type: {b['type']}")
                print(f"  File: {b['file']}")
                print(f"  Date: {b['timestamp']}")
                print(f"  Files: {b['files']}")
        else:
            print("❌ No backups found")
            
    elif args.scan:
        organizer.run_scan_only(target_path)
        
    elif args.prompt:
        organizer.run_prompt_only(target_path)
        
    elif args.execute:
        organizer.run_execute_only(target_path)
        
    else:
        # Full workflow
        organizer.run_full_workflow(target_path, auto_mode=args.auto)

if __name__ == "__main__":
    main()