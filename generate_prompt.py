import json
from scanner import scan_directory, summarize_files_for_llm
from datetime import datetime

MAX_FILES = 30  # limit for token sanity

def generate_gpt_ready_prompt(scan_path, max_snippet_chars=300):
    files = scan_directory(scan_path)
    summarized = summarize_files_for_llm(files, max_snippet_chars)
    summarized = summarized[:MAX_FILES]

    lines = []
    for f in summarized:
        line = (
            f"- **Name**: {f['name']}\n"
            f"  - **Relative Path**: {f['relative_path']}\n"
            f"  - **Extension**: {f['extension']}\n"
            f"  - **Size**: {f['size_kb']} KB\n"
            f"  - **Created**: {f['created']}\n"
            f"  - **Modified**: {f['modified']}\n"
            f"  - **Content Snippet**: {f['content_snippet'][:200].replace(chr(10), ' ')}"
        )
        lines.append(line)

    prompt = f"""
    You are a file organization assistant.

    Given the following files, suggest:
    1. A smart folder structure (e.g., 'Work/Finance', 'Photos', 'School/Assignments')
    2. A new folder path for each file, relative to the root scanned directory
    3. A short reason for each move

    Use content, timestamps, and naming to group meaningfully. Your output should be JSON like:

    {{
    "folders": [ ... ],
    "moves": [
        {{
        "file": "original_filename.ext",
        "relative_path": "original/relative/path.ext",
        "new_path": "SmartFolder/new_filename.ext",
        "reason": "why it belongs here"
        }},
        ...
    ]
    }}

    Files metadata:
    {chr(10).join(lines)}

    Your response:
    """.strip()

    with open("gpt_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print("✅ Prompt saved to gpt_prompt.txt with full metadata.")

if __name__ == "__main__":
    scan_dir = "/Volumes/T7/fileorganizertest"
    generate_gpt_ready_prompt(scan_dir)
