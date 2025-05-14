import os
import json
from pathlib import Path

def scan_directory(directory_path):
    summary = []
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            filepath = Path(root) / filename
            summary.append({
                "name": filename,
                "path": str(filepath),
                "extension": filepath.suffix,
                "size_kb": round(filepath.stat().st_size / 1024, 2),
                "created": filepath.stat().st_ctime,
            })
    return summary


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py /path/to/folder")
        sys.exit(1)
    folder = sys.argv[1]
    print(json.dumps(scan_directory(folder), indent=2))