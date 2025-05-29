import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import hashlib

PLAN_FILE = "data/plan.json"
BACKUP_FILE = "data/backup_manifest.json"

def load_plan(plan_file=PLAN_FILE):
    """Load reorganization plan from JSON file"""
    plan_path = Path(plan_file)
    if not plan_path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_file}")
        
    with open(plan_path, 'r') as f:
        return json.load(f)

def validate_plan(plan, root_path):
    """Validate the reorganization plan"""
    issues = []
    root = Path(root_path).resolve()
    
    # Check for required keys
    if "moves" not in plan:
        issues.append("Missing 'moves' key in plan")
        return issues
        
    # Track destinations to detect conflicts
    destinations = {}
    
    for i, move in enumerate(plan.get("moves", [])):
        # Check required fields
        for field in ["file", "new_path", "reason"]:
            if field not in move:
                issues.append(f"Move {i}: Missing required field '{field}'")
                
        # Check if source exists
        if "relative_path" in move:
            source = root / move["relative_path"]
        else:
            source = root / move["file"]
            
        if not source.exists():
            issues.append(f"Move {i}: Source file not found: {source}")
            
        # Check for destination conflicts
        dest = move.get("new_path", "")
        if dest in destinations:
            issues.append(f"Move {i}: Duplicate destination: {dest}")
        destinations[dest] = i
        
    return issues

def create_backup_manifest(root_path, plan):
    """Create a backup manifest before moving files"""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "root_path": str(root_path),
        "original_state": [],
        "plan_summary": {
            "total_moves": len(plan.get("moves", [])),
            "folders_created": plan.get("folders", [])
        }
    }
    
    root = Path(root_path).resolve()
    
    # Record current state of files to be moved
    for move in plan.get("moves", []):
        if "relative_path" in move:
            source = root / move["relative_path"]
        else:
            source = root / move["file"]
            
        if source.exists():
            # Calculate file hash for verification
            file_hash = calculate_file_hash(source) if source.is_file() else None
            
            manifest["original_state"].append({
                "original_path": str(source.relative_to(root)),
                "new_path": move["new_path"],
                "file_hash": file_hash,
                "size": source.stat().st_size if source.exists() else 0,
                "modified": source.stat().st_mtime if source.exists() else 0
            })
    
    # Save manifest
    os.makedirs("data", exist_ok=True)
    with open(BACKUP_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    return manifest

def calculate_file_hash(filepath, chunk_size=8192):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except:
        return None

def perform_file_moves(root_path, plan, dry_run=False):
    """Execute the file reorganization plan"""
    root = Path(root_path).resolve()
    
    # Validate plan first
    issues = validate_plan(plan, root_path)
    if issues:
        print("❌ Plan validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    # Create backup manifest
    if not dry_run:
        print("📸 Creating backup manifest...")
        create_backup_manifest(root_path, plan)
    
    # Create folders
    folders_created = set()
    for folder in plan.get("folders", []):
        folder_path = root / folder
        if not folder_path.exists():
            if not dry_run:
                os.makedirs(folder_path, exist_ok=True)
            folders_created.add(folder)
            print(f"📁 {'Would create' if dry_run else 'Created'} folder: {folder}")
    
    # Move files
    successful_moves = 0
    failed_moves = []
    
    print(f"\n🚚 {'Simulating' if dry_run else 'Moving'} {len(plan['moves'])} files...\n")
    
    for move in tqdm(plan["moves"], desc="Processing files"):
        try:
            # Determine source path
            if "relative_path" in move:
                source = root / move["relative_path"]
            else:
                source = root / move["file"]
                
            dest = root / move["new_path"]
            
            if not source.exists():
                failed_moves.append({
                    "file": str(source),
                    "error": "Source file not found"
                })
                continue
            
            # Create destination directory
            if not dry_run:
                os.makedirs(dest.parent, exist_ok=True)
            
            # Handle filename conflicts
            if dest.exists() and not dry_run:
                # Rename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{dest.stem}_{timestamp}{dest.suffix}"
                dest = dest.parent / new_name
                print(f"\n⚠️ Renamed to avoid conflict: {new_name}")
            
            # Move the file
            if not dry_run:
                shutil.move(str(source), str(dest))
            
            successful_moves += 1
            
            # Show reason for move (sampling to avoid spam)
            if successful_moves <= 5 or successful_moves % 10 == 0:
                print(f"\n✅ {source.name} → {move['new_path']}")
                print(f"   Reason: {move['reason']}")
                
        except Exception as e:
            failed_moves.append({
                "file": move.get("file", "unknown"),
                "error": str(e)
            })
    
    # Summary
    print(f"\n📊 Organization {'Simulation' if dry_run else 'Complete'}!")
    print(f"✅ Successful moves: {successful_moves}")
    print(f"❌ Failed moves: {len(failed_moves)}")
    print(f"📁 Folders created: {len(folders_created)}")
    
    if failed_moves:
        print("\n⚠️ Failed moves:")
        for fail in failed_moves[:5]:  # Show first 5
            print(f"  - {fail['file']}: {fail['error']}")
        if len(failed_moves) > 5:
            print(f"  ... and {len(failed_moves) - 5} more")
    
    # Save results
    if not dry_run:
        results = {
            "timestamp": datetime.now().isoformat(),
            "successful_moves": successful_moves,
            "failed_moves": failed_moves,
            "folders_created": list(folders_created)
        }
        
        with open("data/organization_results.json", 'w') as f:
            json.dump(results, f, indent=2)
    
    return successful_moves > 0

def cleanup_empty_folders(root_path, dry_run=False):
    """Remove empty folders after reorganization"""
    root = Path(root_path).resolve()
    empty_folders = []
    
    # Find empty folders (bottom-up)
    for folder in sorted(root.rglob("*/"), reverse=True):
        try:
            if not any(folder.iterdir()):
                empty_folders.append(folder)
                if not dry_run:
                    folder.rmdir()
        except:
            pass
    
    if empty_folders:
        print(f"\n🧹 {'Would remove' if dry_run else 'Removed'} {len(empty_folders)} empty folders")
        
    return empty_folders

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python organize.py /path/to/folder [--dry-run]")
        sys.exit(1)
    
    scan_dir = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be moved\n")
    
    try:
        # Load plan
        plan = load_plan()
        
        # Perform moves
        success = perform_file_moves(scan_dir, plan, dry_run=dry_run)
        
        if success and not dry_run:
            # Clean up empty folders
            cleanup_empty_folders(scan_dir, dry_run=dry_run)
            
            print("\n✨ Organization complete!")
            print("💾 Backup manifest saved to: data/backup_manifest.json")
            print("🔄 To revert changes, run: python backup.py --revert")
            
    except FileNotFoundError:
        print("❌ No plan.json found. Please run generate_prompt.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during organization: {e}")
        sys.exit(1)