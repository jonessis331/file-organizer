import os
import shutil
import json
from pathlib import Path
from scanner import scan_directory, summarize_files_for_llm
from tqdm import tqdm

PLAN_FILE = "plan.json"

def load_plan(plan_file):
    with open(plan_file, 'r') as f:
        return json.load(f)

def preserve_organized_folder(path, project_keywords=["project", "app", "repo"]):
    # heuristic: don't split folders with many files or that contain keywords
    file_count = sum(len(files) for _, _, files in os.walk(path))
    name = path.name.lower()
    return file_count > 5 or any(kw in name for kw in project_keywords)

def perform_file_moves(scan_dir, plan):
    root_path = Path(scan_dir).resolve()

    print("\n🚚 Moving files according to plan:\n")

    for move in plan.get("moves", []):
        original_rel_path = move.get("relative_path")
        old_path = root_path / original_rel_path if original_rel_path else root_path / move["file"]
        new_path = root_path / move["new_path"]

        try:
            if not old_path.exists():
                print(f"⚠️ File not found: {old_path}")
                continue

            # Avoid destroying organized folders
            if preserve_organized_folder(old_path.parent):
                print(f"🛑 Skipping '{old_path}' — part of organized folder '{old_path.parent.name}'")
                continue

            os.makedirs(new_path.parent, exist_ok=True)
            shutil.move(str(old_path), str(new_path))
            print(f"✅ Moved '{old_path.name}' → '{move['new_path']}' — {move['reason']}")
        except Exception as e:
            print(f"⚠️ Failed to move {move['file']}: {e}")

if __name__ == "__main__":
    import sys

    # if len(sys.argv) < 2:
    #     print("Usage: python organize.py /path/to/folder")
    #     sys.exit(1)

    # # scan_dir = sys.argv[1]
    # scan_dir = "/Volumes/T7/fileorganizertest"

    # if not os.path.exists(PLAN_FILE):
    #     print(f"❌ No plan file found: {PLAN_FILE}")
    #     sys.exit(1)
    scan_dir = "/Volumes/T7/fileorganizertest"
    plan = load_plan(PLAN_FILE)
    perform_file_moves(scan_dir, plan)

# scan_dir = "/Volumes/T7/fileorganizertest"