import os
import sys
import json

def scan_directory(path):
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                stat = os.stat(full_path)
                result.append({
                    "name": file,
                    "path": full_path,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            except Exception as e:
                result.append({
                    "name": file,
                    "path": full_path,
                    "error": str(e)
                })
    return result

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    scanned_files = scan_directory(folder)
    print(json.dumps(scanned_files))
