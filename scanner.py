import os
import json
from pathlib import Path
from datetime import datetime
from docx import Document
import fitz  # PyMuPDF
from tqdm import tqdm

TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.html', '.css', '.sh', '.java', '.c', '.cpp', '.json', '.csv'
}

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat()

def get_depth(root_path, current_path):
    return len(Path(current_path).relative_to(root_path).parts)

def read_content_snippet(filepath: Path, max_chars=1000):
    try:
        if filepath.suffix.lower() in TEXT_EXTENSIONS:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_chars)

        elif filepath.suffix.lower() == ".pdf":
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
                if len(text) >= max_chars:
                    break
            return text[:max_chars].strip()

        elif filepath.suffix.lower() == ".docx":
            doc = Document(filepath)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            return full_text[:max_chars].strip()

        elif filepath.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            return f"Image file, filename suggests: {filepath.stem}"

        elif filepath.suffix.lower() == ".zip":
            return "Compressed archive — likely a bundle of multiple files"

        elif filepath.suffix == "":
            return f"No extension, possibly a system file — name: {filepath.name}"

        else:
            return f"File: {filepath.name} (type: {filepath.suffix})"
    except Exception as e:
        return f"Error reading file {filepath.name}: {e}"

def scan_directory(directory_path):
    summary = []
    root_path = Path(directory_path).resolve()
    files = [Path(root) / f for root, _, fs in os.walk(root_path) for f in fs]
    print(f"🔍 Total files discovered (pre-filter): {len(files)}")


    for filepath in tqdm(files, desc="Scanning files"):
        if filepath.name.startswith('.') or not filepath.exists():
            continue

        try:
            stat = filepath.stat()
            summary.append({
                "name": filepath.name,
                "relative_path": str(filepath.relative_to(root_path)),
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
        except Exception as e:
            print(f"⚠️ Skipping {filepath.name}: {e}")
        print(f"📄 Found file: {filepath}")

    return summary

def summarize_files_for_llm(files, max_snippet_chars=300):
    return [
        {
            "name": f["name"],
            "relative_path": f["relative_path"],
            "extension": f["extension"],
            "size_kb": f["size_kb"],
            "created": f["created"],
            "modified": f["modified"],
            "content_snippet": (f.get("content_snippet") or "")[:max_snippet_chars].strip()
        }
        for f in files
    ]

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py /path/to/folder")
        sys.exit(1)

    folder = sys.argv[1]
    print(json.dumps(scan_directory(folder), indent=2))
