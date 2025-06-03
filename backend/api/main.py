#!/usr/bin/env python3
"""
FastAPI backend for File Organizer Desktop App
Provides REST API endpoints for the Electron frontend
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    # Import your existing modules
    from backend.core.scanner import scan_directory, analyze_folder_structure
    from backend.core.prompt_generator import generate_konmari_prompt, save_prompt
    from backend.core.organizer import perform_file_moves, load_plan, validate_plan
    from backend.core.backup import create_full_backup, revert_organization, list_backups
    from backend.config.settings import Config
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Make sure all required modules are in the same directory as api.py")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="File Organizer API",
    description="Local API for File Organizer Desktop App",
    version="1.0.0"
)

# Configure CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task storage (in production, use Redis or similar)
tasks: Dict[str, Dict[str, Any]] = {}
scan_results: Dict[str, Any] = {}

# Request/Response Models
class ScanRequest(BaseModel):
    path: str
    max_files: Optional[int] = Field(default=1000, ge=1, le=10000)

class GeneratePromptRequest(BaseModel):
    path: str
    use_cached_scan: Optional[bool] = True

class OrganizePlanRequest(BaseModel):
    path: str
    plan: Dict[str, Any]
    dry_run: Optional[bool] = True

class ExecutePlanRequest(BaseModel):
    path: str
    dry_run: Optional[bool] = False

class BackupRequest(BaseModel):
    path: str
    backup_name: Optional[str] = None

class RevertRequest(BaseModel):
    manifest_file: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 to 1.0
    message: str
    result: Optional[Any] = None
    error: Optional[str] = None

# Utility functions
def create_task(task_type: str) -> str:
    """Create a new task and return its ID"""
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "type": task_type,
        "status": "pending",
        "progress": 0.0,
        "message": f"Initializing {task_type}...",
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    return task_id

def update_task(task_id: str, **kwargs):
    """Update task status"""
    if task_id in tasks:
        tasks[task_id].update(kwargs)
        tasks[task_id]["updated_at"] = datetime.now().isoformat()

# Background task workers
async def scan_directory_async(task_id: str, path: str, max_files: int):
    """Async wrapper for directory scanning"""
    try:
        print(f"🔍 Starting scan for task {task_id} at path: {path}")
        update_task(task_id, status="running", progress=0.1, message="Analyzing folder structure...")
        
        # Run in thread pool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Analyze folder structure in thread
        analysis = await loop.run_in_executor(None, analyze_folder_structure, path)
        print(f"📊 Analysis complete: {analysis['total_files']} files found")
        update_task(task_id, progress=0.3, message=f"Found {analysis['total_files']} files...")
        
        # Since scan_directory doesn't support progress callback in the original implementation,
        # we'll run it without callback and simulate progress
        update_task(task_id, progress=0.5, message="Scanning files...")
        
        # Perform scan in thread
        files = await loop.run_in_executor(None, scan_directory, path, max_files)
        print(f"✅ Scan complete: {len(files)} files scanned")
        
        # Store results
        scan_result = {
            "scan_date": datetime.now().isoformat(),
            "root_path": path,
            "analysis": analysis,
            "files": files
        }
        
        scan_results[task_id] = scan_result
        
        # Save to disk
        os.makedirs("data", exist_ok=True)
        with open("data/scan_results.json", "w") as f:
            json.dump(scan_result, f, indent=2)
        
        update_task(task_id, 
                   status="completed", 
                   progress=1.0, 
                   message=f"Scan complete! Found {len(files)} files to organize.",
                   result={
                       "total_files": len(files),
                       "organized_folders": len(analysis.get("organized_folders", [])),
                       "file_types": analysis.get("file_types", {})
                   })
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Scan failed: {error_details}")
        update_task(task_id, 
                   status="failed", 
                   error=error_details,
                   message=f"Scan failed: {str(e)}")

async def generate_prompt_async(task_id: str, path: str):
    """Async wrapper for prompt generation"""
    try:
        update_task(task_id, status="running", progress=0.2, message="Loading scan results...")
        
        # Generate prompt
        update_task(task_id, progress=0.5, message="Generating organization prompt...")
        prompt = generate_konmari_prompt(path)
        
        # Save prompt
        update_task(task_id, progress=0.8, message="Saving prompt...")
        prompt_file = save_prompt(prompt)
        
        update_task(task_id,
                   status="completed",
                   progress=1.0,
                   message="Prompt generated successfully!",
                   result={
                       "prompt_file": str(prompt_file),
                       "prompt_length": len(prompt),
                       "prompt_preview": prompt[:500] + "..."
                   })
        
    except Exception as e:
        update_task(task_id,
                   status="failed",
                   error=str(e),
                   message=f"Prompt generation failed: {str(e)}")

async def organize_files_async(task_id: str, path: str, dry_run: bool):
    """Async wrapper for file organization"""
    try:
        update_task(task_id, status="running", progress=0.1, message="Loading organization plan...")
        
        # Import here to avoid circular import
        from backend.core.organizer import create_backup_manifest
        
        # Load plan
        plan_response = await load_plan()
        plan =  plan_response['plan'] 
        total_moves = len(plan.get("moves", []))
        
        update_task(task_id, progress=0.2, message=f"Validating {total_moves} moves...")
        
        # Validate plan
        issues = validate_plan(plan, path)
        if issues:
            raise ValueError(f"Plan validation failed: {'; '.join(issues)}")
        
        # Create backup if not dry run
        if not dry_run:
            update_task(task_id, progress=0.3, message="Creating backup manifest...")
            create_backup_manifest(path, plan)
        
        # Execute moves with progress tracking
        update_task(task_id, progress=0.4, message=f"{'Simulating' if dry_run else 'Moving'} files...")
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, perform_file_moves, path, plan, dry_run)
        
        update_task(task_id,
                   status="completed",
                   progress=1.0,
                   message=f"Organization {'simulation' if dry_run else 'completed'} successfully!",
                   result={
                       "dry_run": dry_run,
                       "total_moves": total_moves,
                       "success": result
                   })
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        update_task(task_id,
                   status="failed",
                   error=error_details,
                   message=f"Organization failed: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "version": "1.0.0",
        "message": "File Organizer API is running"
    }

@app.post("/api/scan", response_model=TaskResponse)
async def scan_folder(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start scanning a folder"""
    # Validate path
    path = Path(request.path)
    if not path.exists():
        raise HTTPException(status_code=400, detail="Path does not exist")
    if not path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    # Create task
    task_id = create_task("scan")
    
    # Start background scan
    background_tasks.add_task(
        scan_directory_async,
        task_id,
        str(path),
        request.max_files
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Scan started"
    )

@app.get("/api/scan/{task_id}/results")
async def get_scan_results(task_id: str):
    """Get scan results for a completed scan task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if tasks[task_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Scan not completed")
    
    if task_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan results not found")
    
    return scan_results[task_id]

@app.post("/api/prompt", response_model=TaskResponse)
async def generate_prompt(request: GeneratePromptRequest, background_tasks: BackgroundTasks):
    """Generate organization prompt"""
    # Validate path
    path = Path(request.path)
    if not path.exists():
        raise HTTPException(status_code=400, detail="Path does not exist")
    
    # Check if scan results exist
    if request.use_cached_scan and not Path("data/scan_results.json").exists():
        raise HTTPException(status_code=400, detail="No scan results found. Run scan first.")
    
    # Create task
    task_id = create_task("prompt")
    
    # Start background prompt generation
    background_tasks.add_task(
        generate_prompt_async,
        task_id,
        str(path)
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Prompt generation started"
    )

@app.post("/api/plan/validate")
async def validate_organization_plan(request: OrganizePlanRequest):
    """Validate an organization plan"""
    try:
        issues = validate_plan(request.plan, request.path)
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_moves": len(request.plan.get("moves", [])),
            "folders_to_create": request.plan.get("folders", [])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/plan/save")
async def save_organization_plan(request: OrganizePlanRequest):
    """Save organization plan to disk"""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/plan.json", "w") as f:
            json.dump(request.plan, f, indent=2)
        
        return {
            "success": True,
            "message": "Plan saved successfully",
            "path": "data/plan.json"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plan/load")
async def load_plan():
    """Load the saved organization plan"""
    try:
        plan_path = Path("data/plan.json")
        if not plan_path.exists():
            raise HTTPException(status_code=404, detail="No plan found")
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        return {
            "success": True,
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/organize", response_model=TaskResponse)
async def organize_files(request: ExecutePlanRequest, background_tasks: BackgroundTasks):
    """Execute organization plan"""
    # Validate path
    path = Path(request.path)
    if not path.exists():
        raise HTTPException(status_code=400, detail="Path does not exist")
    
    # Check if plan exists
    if not Path("data/plan.json").exists():
        raise HTTPException(status_code=400, detail="No organization plan found")
    
    # Create task
    task_id = create_task("organize")
    
    # Start background organization
    background_tasks.add_task(
        organize_files_async,
        task_id,
        str(path),
        request.dry_run
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Organization {'simulation' if request.dry_run else 'execution'} started"
    )

@app.get("/api/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get status of a background task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    # Add the task_id to the response
    return TaskStatusResponse(
        task_id=task_id,
        status=task.get("status", "unknown"),
        progress=task.get("progress", 0.0),
        message=task.get("message", ""),
        result=task.get("result"),
        error=task.get("error")
    )

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "type": task["type"],
                "status": task["status"],
                "created_at": task["created_at"],
                "message": task["message"]
            }
            for task_id, task in tasks.items()
        ]
    }

@app.post("/api/backup", response_model=TaskResponse)
async def create_backup(request: BackupRequest):
    """Create a full backup"""
    try:
        # Validate path
        path = Path(request.path)
        if not path.exists():
            raise HTTPException(status_code=400, detail="Path does not exist")
        
        # Create backup synchronously (it's fast enough)
        backup_file = create_full_backup(str(path), request.backup_name)
        
        return TaskResponse(
            task_id="backup_" + str(uuid.uuid4()),
            status="completed",
            message=f"Backup created: {backup_file}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backups")
async def get_backups():
    """List all available backups"""
    try:
        backups = list_backups()
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/revert")
async def revert_changes(request: RevertRequest):
    """Revert organization changes"""
    try:
        # This should be done carefully, perhaps with more confirmation
        success = revert_organization(request.manifest_file)
        return {
            "success": success,
            "message": "Revert completed" if success else "Revert failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_configuration():
    """Get application configuration"""
    return {
        "max_files_to_scan": Config.MAX_FILES_TO_SCAN,
        "max_files_for_prompt": Config.MAX_FILES_FOR_PROMPT,
        "file_categories": {
            "documents": list(Config.DOCUMENT_EXTENSIONS),
            "code": list(Config.CODE_EXTENSIONS),
            "images": list(Config.IMAGE_EXTENSIONS),
            "videos": list(Config.VIDEO_EXTENSIONS),
            "audio": list(Config.AUDIO_EXTENSIONS),
            "archives": list(Config.ARCHIVE_EXTENSIONS)
        },
        "skip_folders": list(Config.SKIP_FOLDERS)
    }

@app.get("/api/openai/status")
async def check_openai_status():
    """Check if OpenAI API is configured"""
    return {
        "configured": Config.OPENAI_API_KEY is not None,
        "model": Config.OPENAI_MODEL if Config.OPENAI_API_KEY else None
    }

# Server-Sent Events for real-time updates
@app.get("/api/events/{task_id}")
async def task_events(task_id: str, request: Request):
    """Stream task updates using Server-Sent Events"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        last_update = None
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
                
            # Check for updates
            if task_id in tasks:
                task = tasks[task_id]
                current_update = task["updated_at"]
                
                # Send update if changed
                if current_update != last_update:
                    last_update = current_update
                    yield f"data: {json.dumps(task)}\n\n"
                
                # Exit if task is complete
                if task["status"] in ["completed", "failed"]:
                    break
            
            # Wait a bit before next check
            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Error handling
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    import traceback
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc() if os.getenv("DEBUG") else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="info"
    )