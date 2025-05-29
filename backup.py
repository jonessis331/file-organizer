import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import hashlib

BACKUP_FILE = "data/backup_manifest.json"
ARCHIVE_DIR = "data/backup_archives"

def load_backup_manifest(manifest_file=BACKUP_FILE):
    """Load the backup manifest"""
    if not Path(manifest_file).exists():
        raise FileNotFoundError(f"Backup manifest not found: {manifest_file}")
        
    with open(manifest_file, 'r') as f:
        return json.load(f)

def verify_file_integrity(filepath, expected_hash):
    """Verify file hasn't been modified using hash"""
    if not filepath.exists() or not expected_hash:
        return False
        
    actual_hash = calculate_file_hash(filepath)
    return actual_hash == expected_hash

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

def revert_organization(manifest_file=BACKUP_FILE, verify_integrity=True):
    """Revert file organization using backup manifest"""
    manifest = load_backup_manifest(manifest_file)
    root_path = Path(manifest["root_path"]).resolve()
    
    print(f"🔄 Reverting organization from: {manifest['timestamp']}")
    print(f"📁 Root path: {root_path}")
    print(f"📊 Files to revert: {len(manifest['original_state'])}\n")
    
    # Confirmation
    response = input("⚠️  This will move files back to their original locations. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Revert cancelled")
        return False
    
    successful_reverts = 0
    failed_reverts = []
    integrity_warnings = []
    
    print("\n🔄 Reverting files...\n")
    
    for entry in tqdm(manifest["original_state"], desc="Reverting files"):
        try:
            current_path = root_path / entry["new_path"]
            original_path = root_path / entry["original_path"]
            
            if not current_path.exists():
                # Try to find file in original location (maybe already reverted)
                if original_path.exists():
                    successful_reverts += 1
                    continue
                else:
                    failed_reverts.append({
                        "file": entry["new_path"],
                        "error": "File not found in current location"
                    })
                    continue
            
            # Verify file integrity if requested
            if verify_integrity and entry.get("file_hash"):
                if not verify_file_integrity(current_path, entry["file_hash"]):
                    integrity_warnings.append({
                        "file": str(current_path),
                        "warning": "File has been modified since organization"
                    })
            
            # Create original directory if needed
            os.makedirs(original_path.parent, exist_ok=True)
            
            # Handle conflicts
            if original_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{original_path.stem}_conflict_{timestamp}{original_path.suffix}"
                backup_path = original_path.parent / backup_name
                shutil.move(str(original_path), str(backup_path))
                print(f"\n⚠️ Conflict resolved: Existing file backed up to {backup_name}")
            
            # Move file back
            shutil.move(str(current_path), str(original_path))
            successful_reverts += 1
            
        except Exception as e:
            failed_reverts.append({
                "file": entry.get("new_path", "unknown"),
                "error": str(e)
            })
    
    # Clean up empty folders created during organization
    print("\n🧹 Cleaning up empty folders...")
    cleanup_count = cleanup_empty_folders(root_path, manifest.get("plan_summary", {}).get("folders_created", []))
    
    # Summary
    print(f"\n📊 Revert Summary:")
    print(f"✅ Successfully reverted: {successful_reverts}")
    print(f"❌ Failed to revert: {len(failed_reverts)}")
    print(f"⚠️  Integrity warnings: {len(integrity_warnings)}")
    print(f"🧹 Empty folders removed: {cleanup_count}")
    
    if failed_reverts:
        print("\n❌ Failed reverts:")
        for fail in failed_reverts[:5]:
            print(f"  - {fail['file']}: {fail['error']}")
        if len(failed_reverts) > 5:
            print(f"  ... and {len(failed_reverts) - 5} more")
    
    if integrity_warnings:
        print("\n⚠️ File integrity warnings:")
        for warning in integrity_warnings[:5]:
            print(f"  - {warning['file']}: {warning['warning']}")
        if len(integrity_warnings) > 5:
            print(f"  ... and {len(integrity_warnings) - 5} more")
    
    # Archive the manifest
    archive_manifest(manifest_file)
    
    return successful_reverts > 0

def cleanup_empty_folders(root_path, created_folders):
    """Remove folders that were created during organization"""
    root = Path(root_path).resolve()
    removed_count = 0
    
    # Sort folders by depth (deepest first)
    folder_paths = [root / folder for folder in created_folders]
    folder_paths.sort(key=lambda p: len(p.parts), reverse=True)
    
    for folder_path in folder_paths:
        try:
            if folder_path.exists() and not any(folder_path.iterdir()):
                folder_path.rmdir()
                removed_count += 1
        except:
            pass
    
    return removed_count

def archive_manifest(manifest_file):
    """Archive the backup manifest after revert"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"backup_manifest_{timestamp}.json"
    archive_path = Path(ARCHIVE_DIR) / archive_name
    
    shutil.move(manifest_file, str(archive_path))
    print(f"\n📦 Manifest archived to: {archive_path}")

def create_full_backup(root_path, backup_name=None):
    """Create a full backup of the directory structure (metadata only)"""
    root = Path(root_path).resolve()
    
    if not backup_name:
        backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    backup = {
        "timestamp": datetime.now().isoformat(),
        "root_path": str(root_path),
        "backup_name": backup_name,
        "files": [],
        "statistics": {
            "total_files": 0,
            "total_size_mb": 0,
            "by_extension": {}
        }
    }
    
    print(f"📸 Creating full backup of directory structure...")
    
    # Scan all files
    for filepath in tqdm(list(root.rglob("*")), desc="Scanning files"):
        if filepath.is_file():
            try:
                stat = filepath.stat()
                rel_path = str(filepath.relative_to(root))
                
                backup["files"].append({
                    "path": rel_path,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "hash": calculate_file_hash(filepath) if stat.st_size < 10*1024*1024 else None
                })
                
                # Update statistics
                backup["statistics"]["total_files"] += 1
                backup["statistics"]["total_size_mb"] += stat.st_size / (1024 * 1024)
                
                ext = filepath.suffix.lower()
                backup["statistics"]["by_extension"][ext] = \
                    backup["statistics"]["by_extension"].get(ext, 0) + 1
                    
            except Exception as e:
                print(f"\n⚠️ Error backing up {filepath}: {e}")
    
    # Save backup
    os.makedirs("data", exist_ok=True)
    backup_file = f"data/{backup_name}.json"
    
    with open(backup_file, 'w') as f:
        json.dump(backup, f, indent=2)
    
    print(f"\n✅ Full backup created: {backup_file}")
    print(f"📊 Total files: {backup['statistics']['total_files']}")
    print(f"💾 Total size: {backup['statistics']['total_size_mb']:.2f} MB")
    
    return backup_file

def list_backups():
    """List all available backups"""
    backups = []
    
    # Check for backup manifests
    if Path(BACKUP_FILE).exists():
        manifest = load_backup_manifest()
        backups.append({
            "type": "Organization Backup",
            "file": BACKUP_FILE,
            "timestamp": manifest["timestamp"],
            "files": len(manifest["original_state"])
        })
    
    # Check for archived manifests
    if Path(ARCHIVE_DIR).exists():
        for archive in Path(ARCHIVE_DIR).glob("*.json"):
            try:
                with open(archive, 'r') as f:
                    data = json.load(f)
                backups.append({
                    "type": "Archived Manifest",
                    "file": str(archive),
                    "timestamp": data["timestamp"],
                    "files": len(data.get("original_state", []))
                })
            except:
                pass
    
    # Check for full backups
    for backup in Path("data").glob("full_backup_*.json"):
        try:
            with open(backup, 'r') as f:
                data = json.load(f)
            backups.append({
                "type": "Full Backup",
                "file": str(backup),
                "timestamp": data["timestamp"],
                "files": data["statistics"]["total_files"]
            })
        except:
            pass
    
    return backups

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup.py --revert              # Revert last organization")
        print("  python backup.py --revert <manifest>   # Revert specific manifest")
        print("  python backup.py --create <path>       # Create full backup")
        print("  python backup.py --list                # List all backups")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--revert":
        manifest_file = sys.argv[2] if len(sys.argv) > 2 else BACKUP_FILE
        try:
            success = revert_organization(manifest_file)
            if success:
                print("\n✅ Revert completed successfully!")
            else:
                print("\n❌ Revert failed or was cancelled")
        except FileNotFoundError:
            print("❌ No backup manifest found. Cannot revert.")
            print("💡 Tip: Backup manifests are created when you run organize.py")
        except Exception as e:
            print(f"❌ Error during revert: {e}")
            
    elif command == "--create" and len(sys.argv) > 2:
        root_path = sys.argv[2]
        backup_name = sys.argv[3] if len(sys.argv) > 3 else None
        create_full_backup(root_path, backup_name)
        
    elif command == "--list":
        backups = list_backups()
        if backups:
            print("\n📦 Available backups:\n")
            for backup in backups:
                print(f"Type: {backup['type']}")
                print(f"File: {backup['file']}")
                print(f"Date: {backup['timestamp']}")
                print(f"Files: {backup['files']}")
                print("-" * 50)
        else:
            print("❌ No backups found")
    else:
        print("❌ Invalid command. Use --revert, --create, or --list")