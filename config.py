"""
Configuration settings for the File Organizer
"""

import os
from pathlib import Path

class Config:
    """Configuration settings for the file organizer"""
    
    # API Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4-turbo-preview"
    
    # Scanning Settings
    MAX_FILES_TO_SCAN = 1000  # Maximum files to scan
    MAX_FILES_FOR_PROMPT = 50  # Maximum files to include in prompt
    MAX_CONTENT_SNIPPET_LENGTH = 200  # Characters
    MAX_FILE_SIZE_FOR_CONTENT = 100 * 1024 * 1024  # 100MB
    
    # Organization Settings
    PRESERVE_FOLDER_THRESHOLD = 0.8  # 80% similarity to consider organized
    MIN_FILES_FOR_ORGANIZED_FOLDER = 3
    
    # File Type Categories
    DOCUMENT_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', 
        '.tex', '.wpd', '.md'
    }
    
    CODE_EXTENSIONS = {
        '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', 
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.r', '.m', '.sh', '.bat', '.ps1', '.sql', '.html',
        '.css', '.jsx', '.tsx', '.vue', '.json', '.xml', '.yaml'
    }
    
    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', 
        '.ico', '.tiff', '.webp', '.heic', '.raw'
    }
    
    VIDEO_EXTENSIONS = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
        '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'
    }
    
    AUDIO_EXTENSIONS = {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', 
        '.m4a', '.opus', '.ape'
    }
    
    ARCHIVE_EXTENSIONS = {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', 
        '.xz', '.iso', '.dmg'
    }
    
    # Folders to skip
    SKIP_FOLDERS = {
        '.git', '.svn', '.hg', '.bzr',
        'node_modules', '__pycache__', '.vscode', '.idea',
        'venv', 'env', '.env', 'virtualenv',
        'dist', 'build', 'target', 'out', 'bin', 'obj',
        '.pytest_cache', '.mypy_cache', '.tox',
        'coverage', '.coverage', 'htmlcov',
        '.DS_Store', 'Thumbs.db', 'desktop.ini'
    }
    
    # Project indicators (files that indicate a project root)
    PROJECT_INDICATORS = {
        # Build files
        'package.json', 'package-lock.json', 'yarn.lock',
        'requirements.txt', 'Pipfile', 'poetry.lock', 'setup.py',
        'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
        'CMakeLists.txt', 'Makefile', 'rakefile',
        
        # Config files
        '.gitignore', '.gitattributes', 'README.md', 'LICENSE',
        'Dockerfile', 'docker-compose.yml', '.dockerignore',
        '.editorconfig', '.eslintrc', '.prettierrc',
        
        # IDE files
        '.project', '.classpath', '*.sln', '*.xcodeproj'
    }
    
    # Organization Categories
    DEFAULT_CATEGORIES = {
        "Work": {
            "Documents": ["Reports", "Presentations", "Spreadsheets"],
            "Projects": ["Active", "Completed", "Archive"],
            "Communications": ["Emails", "Messages", "Meeting_Notes"]
        },
        "Personal": {
            "Documents": ["Financial", "Medical", "Legal", "Education"],
            "Media": ["Photos", "Videos", "Music"],
            "Hobbies": []
        },
        "System": {
            "Configurations": ["AppSettings", "Backups"],
            "Downloads": ["Software", "Drivers"],
            "Temp": []
        },
        "Archive": {
            "Old_Projects": [],
            "Backups": [],
            "Legacy": []
        }
    }
    
    # Backup Settings
    BACKUP_HASH_SIZE_LIMIT = 10 * 1024 * 1024  # Only hash files < 10MB
    ARCHIVE_BACKUPS_AFTER_DAYS = 30
    
    # UI Settings
    PROGRESS_BAR_ENABLED = True
    COLORED_OUTPUT = True
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/file_organizer.log"
    
    @classmethod
    def get_file_category(cls, extension):
        """Get the category for a file extension"""
        ext = extension.lower()
        
        if ext in cls.DOCUMENT_EXTENSIONS:
            return "Documents"
        elif ext in cls.CODE_EXTENSIONS:
            return "Code"
        elif ext in cls.IMAGE_EXTENSIONS:
            return "Images"
        elif ext in cls.VIDEO_EXTENSIONS:
            return "Videos"
        elif ext in cls.AUDIO_EXTENSIONS:
            return "Audio"
        elif ext in cls.ARCHIVE_EXTENSIONS:
            return "Archives"
        else:
            return "Other"
    
    @classmethod
    def is_project_file(cls, filename):
        """Check if a file indicates a project root"""
        return filename in cls.PROJECT_INDICATORS or \
               any(filename.endswith(indicator) for indicator in cls.PROJECT_INDICATORS 
                   if '*' in indicator)
    
    @classmethod
    def should_skip_folder(cls, folder_name):
        """Check if a folder should be skipped"""
        return folder_name in cls.SKIP_FOLDERS
    
    @classmethod
    def get_suggested_folder_structure(cls):
        """Get the default suggested folder structure"""
        return cls.DEFAULT_CATEGORIES
    
    @classmethod
    def validate_api_key(cls):
        """Check if API key is configured"""
        return bool(cls.OPENAI_API_KEY)
    
    @classmethod
    def get_all_settings(cls):
        """Get all configuration settings as a dictionary"""
        settings = {}
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                settings[attr] = getattr(cls, attr)
        return settings

# Create a singleton instance
config = Config()