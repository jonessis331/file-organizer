import os
import json
from pathlib import Path
from datetime import datetime

TEXT_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.html', '.css', '.sh', '.java', '.c', '.cpp', '.json', '.csv'}

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat()

def get_depth(root_path, current_path):
    return len(Path(current_path).relative_to(root_path).parts)

def read_content_snippet(filepath, max_chars=1000):
    try:
        if filepath.suffix.lower() in TEXT_EXTENSIONS:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_chars)
    except:
        pass
    return None

def scan_directory(directory_path):
    summary = []
    root_path = Path(directory_path).resolve()

    for root, dirs, files in os.walk(root_path):
        for filename in files:
            filepath = Path(root) / filename

            # skip hidden/system files
            if filename.startswith('.') or not filepath.exists():
                continue

            stat = filepath.stat()
            summary.append({
                "name": filename,
                "path": str(filepath),
                "extension": filepath.suffix,
                "size_kb": round(stat.st_size / 1024, 2),
                "created": format_timestamp(stat.st_ctime),
                "modified": format_timestamp(stat.st_mtime),
                "accessed": format_timestamp(stat.st_atime),
                "directory": filepath.parent.name,
                "depth": get_depth(root_path, filepath.parent),
                "content_snippet": read_content_snippet(filepath)
            })

    return summary

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py /path/to/folder")
        sys.exit(1)
    folder = sys.argv[1]
    print(json.dumps(scan_directory(folder), indent=2))
