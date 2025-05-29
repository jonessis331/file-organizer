# 🗂️ Intelligent File Organizer

An AI-powered desktop application that intelligently reorganizes your messy folders using the KonMari method. It scans your files, understands their content and purpose, and creates a clean, intuitive folder structure.

## ✨ Features

- **Smart Scanning**: Recursively scans folders while preserving already-organized areas
- **Content Analysis**: Reads file content (PDFs, documents, code) to understand purpose
- **AI-Powered Planning**: Uses OpenAI/Claude to create intelligent organization plans
- **Safe Execution**: Dry-run mode, automatic backups, and full revert capability
- **Project Preservation**: Automatically detects and preserves project folders (Git repos, etc.)
- **KonMari Principles**: Organizes by purpose and "sparks joy" with clear categories

## 🚀 Quick Start

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/file-organizer.git
cd file-organizer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up OpenAI API key for automatic mode:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

**Full workflow (interactive):**

```bash
python main.py /path/to/messy/folder
```

**Step-by-step workflow:**

```bash
# Step 1: Scan the directory
python main.py /path/to/folder --scan

# Step 2: Generate organization prompt
python main.py /path/to/folder --prompt

# Step 3: Copy prompt to ChatGPT/Claude, get JSON response, save to data/plan.json

# Step 4: Execute the organization plan
python main.py /path/to/folder --execute
```

**Automatic mode (requires OpenAI API key):**

```bash
python main.py /path/to/folder --auto
```

## 📁 How It Works

1. **Scanning Phase**

   - Analyzes folder structure
   - Detects already-organized areas (projects, photo albums, etc.)
   - Extracts file metadata and content snippets
   - Identifies file types and purposes

2. **Planning Phase**

   - Generates a detailed prompt with file information
   - Sends to AI (OpenAI API or manual copy/paste)
   - AI creates a reorganization plan following KonMari principles
   - Plan includes new folder structure and move reasons

3. **Execution Phase**

   - Reviews the plan with dry-run option
   - Creates backup manifest before moving files
   - Moves files to new locations
   - Cleans up empty folders

4. **Safety Features**
   - Full backup before any changes
   - Dry-run mode to preview changes
   - Complete revert capability
   - Preserves organized folders
   - Handles naming conflicts

## 🛠️ Advanced Usage

### Individual Commands

**Scan only:**

```bash
python scanner.py /path/to/folder
```

**Generate prompt only:**

```bash
python generate_prompt.py /path/to/folder
```

**Execute existing plan:**

```bash
python organize.py /path/to/folder [--dry-run]
```

**Backup operations:**

```bash
# Create full backup
python backup.py --create /path/to/folder

# List all backups
python backup.py --list

# Revert last organization
python backup.py --revert

# Revert specific backup
python backup.py --revert path/to/backup_manifest.json
```

### Configuration

Edit `config.py` to customize:

- File type categories
- Folders to skip
- Organization categories
- API settings
- Scanning limits

### Example Workflow

```bash
# 1. Start with a messy Downloads folder
$ python main.py ~/Downloads

🗂️  File Organizer - Full Workflow
📁 Target: /Users/john/Downloads
==================================================

📊 Step 1: Analyzing directory structure...
✅ Found 342 files
📁 Organized folders detected: 2

💾 Create a safety backup before proceeding? [y/N]: y

📸 Creating safety backup...
✅ Backup saved to: data/full_backup_20250528_143022.json

🔍 Step 2: Scanning files...
✅ Scanned 342 files

🤖 Step 3: Generating organization plan...
📝 Prompt saved to: data/gpt_prompt.txt

# 2. Copy prompt to ChatGPT/Claude, get JSON response
# 3. Save response to data/plan.json
# 4. Continue...

✅ Have you saved the plan to data/plan.json? [y/N]: y

📋 Step 4: Reviewing organization plan...
✅ Plan loaded: 285 files to move
📁 New folders to create: 12

📄 Sample moves:
  • Invoice_2024.pdf → Work/Documents/Finance/Invoice_2024.pdf
    Reason: Financial document for business records
  • vacation_photo.jpg → Personal/Media/Photos/2024/vacation_photo.jpg
    Reason: Personal photo from 2024
  ... and 280 more moves

🚀 Execute the organization plan? [y/N]: y
📊 Perform a dry run first? [Y/n]: y

🔍 Performing dry run...
[... dry run output ...]

✅ Dry run complete. Proceed with actual organization? [y/N]: y

🚀 Executing organization plan...
[====================================] 100%

✨ Organization completed successfully!
💾 Backup manifest saved to: data/backup_manifest.json
🔄 To revert: python backup.py --revert
```

## 📊 Organization Principles

The AI organizer follows these KonMari-inspired principles:

1. **Purpose-Based Categories**: Groups files by their intended use, not just type
2. **Intuitive Structure**: Creates folders that make sense at a glance
3. **Time-Based Organization**: Uses dates for time-sensitive content (photos, projects)
4. **Archive Old Items**: Moves inactive files to archive folders
5. **Preserve Projects**: Keeps project folders intact (Git repos, node modules, etc.)

### Example Output Structure

```
📁 Organized_Folder/
├── 📁 Work/
│   ├── 📁 Documents/
│   │   ├── 📁 Finance/
│   │   ├── 📁 Reports/
│   │   └── 📁 Presentations/
│   ├── 📁 Projects/
│   │   ├── 📁 Active/
│   │   └── 📁 Completed/
│   └── 📁 Communications/
├── 📁 Personal/
│   ├── 📁 Documents/
│   ├── 📁 Media/
│   │   ├── 📁 Photos/2024/
│   │   └── 📁 Videos/
│   └── 📁 Hobbies/
├── 📁 System/
│   ├── 📁 Configurations/
│   └── 📁 Downloads/
└── 📁 Archive/
    ├── 📁 Old_Projects/
    └── 📁 Backups/
```

## 🔧 Troubleshooting

### Common Issues

**"No plan.json found"**

- Make sure you've completed the prompt generation step
- Verify the JSON response from AI is saved in `data/plan.json`

**"Failed to move files"**

- Check file permissions
- Ensure no files are open in other applications
- Run with `--dry-run` first to identify issues

**"API key not found"**

- Set environment variable: `export OPENAI_API_KEY="sk-..."`
- Or use manual mode (copy/paste to ChatGPT)

### Safety Tips

1. Always create a backup before organizing large folders
2. Use dry-run mode first
3. Start with a test folder before organizing important data
4. Keep the backup manifest until you're satisfied with results

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Format code
black *.py

# Type checking
mypy *.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Marie Kondo's KonMari Method™
- Built with OpenAI/Anthropic APIs
- Uses PyMuPDF for PDF processing

## 📞 Support

- Create an issue for bug reports
- Check existing issues before creating new ones
- Provide detailed information about your environment

---

Made with ❤️ by developers who hate messy folders
