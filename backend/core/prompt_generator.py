import json
import os
from pathlib import Path
from datetime import datetime
from backend.core.scanner import scan_directory, summarize_files_for_llm, analyze_folder_structure

# Configuration
MAX_FILES = 50  # Adjust based on token limits
MAX_SNIPPET_CHARS = 150

def generate_konmari_prompt(scan_path, max_files=MAX_FILES):
    """Generate an optimized prompt following KonMari principles"""
    
     # Load organization memory
    memory = load_organization_memory(scan_path)
     # Add memory context to prompt
    memory_context = ""
    if memory:
        memory_context = f"""
    **Previous Organization Context:**
    - Last organized: {memory['timestamp']}
    - Existing folder structure: {', '.join(memory['folders_created'])}
    - Known patterns: {json.dumps(memory['organization_patterns'], indent=2)}
    
    Please maintain consistency with the existing organization structure and extend it for new files.
    """

    # Load or generate scan results
    scan_results_path = Path("data/scan_results.json")
    
    if scan_results_path.exists():
        print("📂 Loading existing scan results...")
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)
        files = scan_data["files"]
        analysis = scan_data["analysis"]
    else:
        print("🔍 Scanning directory...")
        analysis = analyze_folder_structure(scan_path)
        files = scan_directory(scan_path, max_files=max_files)
        
    # Summarize files for LLM
    summarized = summarize_files_for_llm(files, MAX_SNIPPET_CHARS)
    
    # Sample files if too many
    if len(summarized) > max_files:
        print(f"📊 Sampling {max_files} files from {len(summarized)} total...")
        # Take a diverse sample
        summarized = sample_diverse_files(summarized, max_files)
    
    # Build file listing
    file_listing = []
    for f in summarized:
        snippet = f['content_snippet'].replace('\n', ' ').strip()
        if len(snippet) > 100:
            snippet = snippet[:97] + "..."
            
        file_entry = f"""- **{f['name']}**
        Path: {f['relative_path']}
        Type: {f['extension'] or 'no-ext'} | Size: {f['size_kb']}KB
        Modified: {f['modified'][:10]}
        Content: {snippet}"""
        file_listing.append(file_entry)
    
    # Create the prompt
    prompt = f"""You are an expert file organization assistant using the KonMari Method principles.
    {memory_context}

    **Current Situation:**
    - Root directory has {len(files)} files needing organization
    - Found {len(analysis['organized_folders'])} already well-organized folders to preserve
    - Most common file types: {', '.join(get_top_extensions(analysis['file_types'], 5))}

    **Organization Principles:**
    1. **Joy & Purpose**: Group files by their purpose and usage intent
    2. **Categories over Location**: Create clear category folders (Work, Personal, Archive, etc.)
    3. **Consolidation**: Merge similar/duplicate content intelligently
    4. **Preservation**: Keep these organized folders intact: {', '.join(analysis['organized_folders'][:5])}
    5. **Clarity**: Use clear, descriptive folder names that "spark joy"

    **Your Task:**
    Create a reorganization plan 
    that:
    - Groups files into intuitive categories based on content and purpose
    - Preserves existing well-organized project folders
    - Creates a clean, navigable structure
    - Provides clear reasoning for each move

    **Output Format (JSON):**
    {{
        "folders": [
            "Work/Documents",
            "Work/Projects/Active",
            "Personal/Photos/2024",
            "Archive/Old_Projects",
            "Resources/Templates",
            // ... more folders
        ],
        "moves": [
            {{
                "file": "filename.ext",
                "relative_path": "current/path/filename.ext",
                "new_path": "Work/Documents/filename.ext",
                "reason": "Work-related document based on content about project planning"
            }},
            // ... more moves
        ],
        "preserve": [
            // Folders that should not be reorganized
        ]
    }}

    **Files to Organize:**
    {chr(10).join(file_listing)}

    **Important Notes:**
    - For Git repositories (.git folders), keep the parent project folder intact
    - Group related files even if they're in different locations
    - Use dates in folder names when relevant (e.g., "Photos/2024-05-Hawaii")
    - Create an "Archive" folder for old/inactive items
    - Suggest "Review" folder for items needing user decision

    Generate the complete reorganization plan:"""

    return prompt

def sample_diverse_files(files, target_count):
    """Sample diverse files to get good representation"""
    # Group by extension
    by_extension = {}
    for f in files:
        ext = f['extension'] or 'no-ext'
        if ext not in by_extension:
            by_extension[ext] = []
        by_extension[ext].append(f)
    
    sampled = []
    
    # First, take at least one of each type
    for ext, ext_files in by_extension.items():
        if len(sampled) < target_count:
            sampled.append(ext_files[0])
    
    # Then add more files proportionally
    remaining = target_count - len(sampled)
    if remaining > 0:
        # Sort extensions by frequency
        sorted_exts = sorted(by_extension.items(), key=lambda x: len(x[1]), reverse=True)
        
        while len(sampled) < target_count and any(len(files) > 1 for _, files in sorted_exts):
            for ext, ext_files in sorted_exts:
                if len(ext_files) > 1 and len(sampled) < target_count:
                    # Take next file not already sampled
                    for f in ext_files[1:]:
                        if f not in sampled:
                            sampled.append(f)
                            break
    
    return sampled[:target_count]

def load_organization_memory(folder_path):
    """Load previous organization schema"""
    memory_file = Path(folder_path) / '.file_organizer_memory.json'
    if memory_file.exists():
        with open(memory_file, 'r') as f:
            return json.load(f)
    return None

def save_organization_memory(folder_path, plan):
    """Save organization schema for future reference"""
    memory = {
        'timestamp': datetime.now().isoformat(),
        'folders_created': plan.get('folders', []),
        'organization_patterns': {}
    }
    
    # Extract patterns from moves
    for move in plan.get('moves', []):
        file_type = Path(move['file']).suffix
        dest_folder = '/'.join(move['new_path'].split('/')[:-1])
        
        if file_type not in memory['organization_patterns']:
            memory['organization_patterns'][file_type] = []
        if dest_folder not in memory['organization_patterns'][file_type]:
            memory['organization_patterns'][file_type].append(dest_folder)
    
    memory_file = Path(folder_path) / '.file_organizer_memory.json'
    with open(memory_file, 'w') as f:
        json.dump(memory, f, indent=2)


def get_top_extensions(file_types, n=5):
    """Get top N file extensions by count"""
    sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
    return [f"{ext}({count})" for ext, count in sorted_types[:n]]

def save_prompt(prompt, filename="gpt_prompt.txt"):
    """Save prompt to file"""
    os.makedirs("data", exist_ok=True)
    filepath = Path("data") / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    return filepath

def generate_and_send_prompt(scan_path, api_key=None):
    """Generate prompt and optionally send to OpenAI"""
    prompt = generate_konmari_prompt(scan_path)
    
    # Save prompt
    prompt_file = save_prompt(prompt)
    print(f"\n✅ Prompt saved to: {prompt_file}")
    print(f"📝 Prompt length: {len(prompt)} characters")
    
    if api_key:
        print("\n🤖 Sending to OpenAI API...")
        response = send_to_openai(prompt, api_key)
        if response:
            # Save plan
            plan_path = Path("data/plan.json")
            with open(plan_path, "w") as f:
                json.dump(response, f, indent=2)
            print(f"✅ Plan saved to: {plan_path}")
            return response
    else:
        print("\n📋 To use this prompt:")
        print("1. Copy the content from data/gpt_prompt.txt")
        print("2. Paste into ChatGPT or Claude")
        print("3. Save the JSON response to data/plan.json")
        print("\n💡 Or set OPENAI_API_KEY environment variable to automate")
    
    return None

def send_to_openai(prompt, api_key):
    """Send prompt to OpenAI and get response"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a file organization expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
        
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_prompt.py /path/to/folder [--send]")
        print("  Add --send flag to automatically send to OpenAI API")
        sys.exit(1)
    
    scan_dir = sys.argv[1]
    send_to_api = "--send" in sys.argv
    
    # Check for API key if sending
    api_key = None
    if send_to_api:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ OPENAI_API_KEY not found in environment")
            send_to_api = False
    
    # Generate prompt
    generate_and_send_prompt(scan_dir, api_key if send_to_api else None)