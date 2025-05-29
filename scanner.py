import os
import json
from pathlib import Path
from datetime import datetime
from docx import Document
import fitz  # PyMuPDF
from tqdm import tqdm
import mimetypes

TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.html', '.css', '.sh', '.java', '.c', '.cpp', 
    '.json', '.csv', '.xml', '.yaml', '.yml', '.ini', '.conf', '.log', '.sql',
    '.r', '.m', '.go', '.rs', '.swift', '.kt', '.scala', '.rb', '.php', '.pl'
}

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}
ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}

# Folders to skip entirely
SKIP_FOLDERS = {
    '.git', 'node_modules', '__pycache__', '.vscode', '.idea', 
    'venv', 'env', '.env', 'dist', 'build', '.pytest_cache',
    '.mypy_cache', '.tox', 'coverage', '.coverage'
}

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat()

def get_depth(root_path, current_path):
    try:
        return len(Path(current_path).relative_to(root_path).parts)
    except ValueError:
        return 0

def should_skip_path(path: Path) -> bool:
    """Check if path should be skipped based on rules"""
    # Skip hidden files/folders
    if path.name.startswith('.'):
        return True
    
    # Skip system folders
    for skip in SKIP_FOLDERS:
        if skip in path.parts:
            return True
    
    # Skip empty files (except certain types)
    if path.is_file() and path.stat().st_size == 0 and path.suffix not in {'.txt', '.md'}:
        return True
        
    return False

def read_content_snippet(filepath: Path, max_chars=500):
    """Extract meaningful content snippet from file"""
    try:
        mime_type, _ = mimetypes.guess_type(str(filepath))
        
        if filepath.suffix.lower() in TEXT_EXTENSIONS:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
                # Clean up whitespace
                content = ' '.join(content.split())
                return content[:max_chars]

        elif filepath.suffix.lower() == ".pdf":
            doc = fitz.open(filepath)
            text = ""
            for i, page in enumerate(doc):
                if i >= 2:  # Only first 2 pages
                    break
                text += page.get_text()
                if len(text) >= max_chars:
                    break
            doc.close()
            return ' '.join(text[:max_chars].split())

        elif filepath.suffix.lower() in {".docx", ".doc"}:
            doc = Document(filepath)
            full_text = "\n".join([para.text for para in doc.paragraphs[:5]])
            return ' '.join(full_text[:max_chars].split())

        elif filepath.suffix.lower() in IMAGE_EXTENSIONS:
            return f"[Image: {filepath.stem}]"

        elif filepath.suffix.lower() in VIDEO_EXTENSIONS:
            return f"[Video: {filepath.stem}]"
            
        elif filepath.suffix.lower() in AUDIO_EXTENSIONS:
            return f"[Audio: {filepath.stem}]"

        elif filepath.suffix.lower() in ARCHIVE_EXTENSIONS:
            return f"[Archive: {filepath.name}]"

        elif filepath.suffix == "":
            # Try to read as text for files without extension
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(100)
                    if content.isprintable():
                        return content[:max_chars]
            except:
                pass
            return f"[No extension: {filepath.name}]"

        else:
            return f"[{filepath.suffix.upper()[1:]} file: {filepath.name}]"
            
    except Exception as e:
        return f"[Error reading: {str(e)[:50]}]"

def is_organized_folder(folder_path: Path, threshold=0.8) -> bool:
    """Detect if a folder is already well-organized"""
    try:
        files = list(folder_path.rglob("*"))
        if len(files) < 3:
            return False
            
        # Check for project indicators
        project_indicators = {
            'package.json', 'requirements.txt', 'setup.py', 'Cargo.toml',
            'go.mod', 'pom.xml', 'build.gradle', 'CMakeLists.txt',
            'Makefile', 'README.md', 'LICENSE', '.gitignore'
        }
        
        file_names = {f.name for f in files if f.is_file()}
        if any(indicator in file_names for indicator in project_indicators):
            return True
            
        # Check extension consistency
        extensions = [f.suffix for f in files if f.is_file() and f.suffix]
        if extensions:
            most_common_ext_count = max(extensions.count(ext) for ext in set(extensions))
            if most_common_ext_count / len(extensions) >= threshold:
                return True
                
        # Check naming patterns
        names = [f.stem for f in files if f.is_file()]
        if len(names) > 3:
            # Check for common prefixes or patterns
            common_prefix = os.path.commonprefix(names)
            if len(common_prefix) > 3:
                return True
                
        return False
        
    except Exception:
        return False

def scan_directory(directory_path, max_files=None, progress_callback=None):
    """Scan directory and return file metadata"""
    summary = []
    root_path = Path(directory_path).resolve()
    
    # Get all files first (for progress bar)
    all_files = []
    for root, dirs, files in os.walk(root_path):
        # Remove folders to skip from dirs in-place
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        
        root_p = Path(root)
        if should_skip_path(root_p):
            continue
            
        for f in files:
            filepath = root_p / f
            if not should_skip_path(filepath):
                all_files.append(filepath)
    
    print(f"🔍 Found {len(all_files)} files to scan")
    
    # Check for organized folders
    organized_folders = set()
    for folder in root_path.rglob("*/"):
        if is_organized_folder(folder):
            organized_folders.add(folder)
            print(f"📁 Detected organized folder: {folder.relative_to(root_path)}")
    
    # Scan files
    for filepath in tqdm(all_files[:max_files] if max_files else all_files, 
                        desc="Scanning files", 
                        disable=progress_callback is not None):
        
        # Skip files in organized folders
        if any(org_folder in filepath.parents for org_folder in organized_folders):
            continue
            
        try:
            stat = filepath.stat()
            
            # Skip very large files (>100MB) for content reading
            read_content = stat.st_size < 100 * 1024 * 1024
            
            file_info = {
                "name": filepath.name,
                "relative_path": str(filepath.relative_to(root_path)),
                "path": str(filepath),
                "extension": filepath.suffix.lower(),
                "size_kb": round(stat.st_size / 1024, 2),
                "created": format_timestamp(stat.st_ctime),
                "modified": format_timestamp(stat.st_mtime),
                "accessed": format_timestamp(stat.st_atime),
                "directory": filepath.parent.name,
                "depth": get_depth(root_path, filepath.parent),
                "content_snippet": read_content_snippet(filepath) if read_content else "[File too large]"
            }
            
            summary.append(file_info)
            
            if progress_callback:
                progress_callback(file_info)
                
        except Exception as e:
            print(f"⚠️ Error scanning {filepath.name}: {e}")
    
    return summary

def summarize_files_for_llm(files, max_snippet_chars=200):
    """Create compact summary for LLM prompt"""
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

def analyze_folder_structure(scan_path):
    """Analyze existing folder structure to preserve organized areas"""
    root_path = Path(scan_path).resolve()
    analysis = {
        "total_files": 0,
        "organized_folders": [],
        "file_types": {},
        "suggestions": []
    }
    
    for folder in root_path.rglob("*/"):
        if should_skip_path(folder):
            continue
            
        if is_organized_folder(folder):
            rel_path = str(folder.relative_to(root_path))
            analysis["organized_folders"].append(rel_path)
            
    # Count file types
    for file in root_path.rglob("*"):
        if file.is_file() and not should_skip_path(file):
            analysis["total_files"] += 1
            ext = file.suffix.lower()
            analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
            
    return analysis

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py /path/to/folder")
        sys.exit(1)

    folder = sys.argv[1]
    
    # Analyze structure first
    print("\n📊 Analyzing folder structure...")
    analysis = analyze_folder_structure(folder)
    print(f"Total files: {analysis['total_files']}")
    print(f"Organized folders found: {len(analysis['organized_folders'])}")
    
    # Scan directory
    files = scan_directory(folder)
    
    # Save results
    output = {
        "scan_date": datetime.now().isoformat(),
        "root_path": folder,
        "analysis": analysis,
        "files": files
    }
    
    with open("data/scan_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        
    print(f"\n✅ Scan complete! Found {len(files)} files to organize")
    print(f"📄 Results saved to data/scan_results.json")