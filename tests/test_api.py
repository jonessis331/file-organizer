import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#!/usr/bin/env python3
"""
Test script for the FastAPI backend
"""

import requests
import json
import time
import sys
from pathlib import Path

API_BASE = "http://localhost:8765"

def test_health():
    """Test API health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/")
    
    print(f"Status: {response.status_code}")
    print(f"Raw response: {response.text}")

    print(f"Response: {response.json()}")
    print("✅ Health check passed\n")

def test_scan(path):
    """Test folder scanning"""
    print(f"🔍 Testing scan endpoint with path: {path}")
    
    # Start scan
    response = requests.post(f"{API_BASE}/api/scan", json={
        "path": path,
        "max_files": 100
    })
    
    if response.status_code != 200:
        print(f"❌ Scan failed: {response.text}")
        return None
        
    data = response.json()
    task_id = data["task_id"]
    print(f"✅ Scan started with task_id: {task_id}")
    
    # Poll for completion
    print("⏳ Waiting for scan to complete...")
    max_attempts = 30  # 30 seconds max
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{API_BASE}/api/task/{task_id}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get task status: {response.text}")
            return None
            
        task = response.json()
        
        print(f"   Status: {task['status']} - Progress: {task['progress']*100:.1f}% - {task['message']}")
        
        if task["status"] == "completed":
            print(f"✅ Scan completed! Found {task['result']['total_files']} files")
            return task_id
        elif task["status"] == "failed":
            print(f"❌ Scan failed: {task['error']}")
            return None
            
        time.sleep(1)
        attempt += 1
    
    print("❌ Scan timed out")
    return None

def test_prompt_generation(path):
    """Test prompt generation"""
    print(f"📝 Testing prompt generation...")
    
    response = requests.post(f"{API_BASE}/api/prompt", json={
        "path": path,
        "use_cached_scan": True
    })
    
    if response.status_code != 200:
        print(f"❌ Prompt generation failed: {response.text}")
        return
        
    data = response.json()
    task_id = data["task_id"]
    print(f"✅ Prompt generation started with task_id: {task_id}")
    
    # Poll for completion
    print("⏳ Waiting for prompt generation...")
    while True:
        response = requests.get(f"{API_BASE}/api/task/{task_id}")
        task = response.json()
        
        print(f"   Status: {task['status']} - Progress: {task['progress']*100:.1f}%")
        
        if task["status"] == "completed":
            print(f"✅ Prompt generated! Length: {task['result']['prompt_length']} chars")
            print(f"   Saved to: {task['result']['prompt_file']}")
            return True
        elif task["status"] == "failed":
            print(f"❌ Prompt generation failed: {task['error']}")
            return False
            
        time.sleep(1)

def test_plan_validation():
    """Test plan validation"""
    print("🔍 Testing plan validation...")
    
    # Create a test plan
    test_plan = {
        "folders": ["TestFolder"],
        "moves": [
            {
                "file": "test.txt",
                "relative_path": "test.txt",
                "new_path": "TestFolder/test.txt",
                "reason": "Test move"
            }
        ]
    }
    
    response = requests.post(f"{API_BASE}/api/plan/validate", json={
        "path": ".",
        "plan": test_plan
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Plan validation: {'Valid' if result['valid'] else 'Invalid'}")
        if not result['valid']:
            print(f"   Issues: {result['issues']}")
    else:
        print(f"❌ Validation failed: {response.text}")

def test_config():
    """Test configuration endpoint"""
    print("⚙️  Testing configuration endpoint...")
    
    response = requests.get(f"{API_BASE}/api/config")
    if response.status_code == 200:
        config = response.json()
        print(f"✅ Configuration loaded:")
        print(f"   Max files to scan: {config['max_files_to_scan']}")
        print(f"   File categories: {len(config['file_categories'])} categories")
        print(f"   Skip folders: {len(config['skip_folders'])} folders")
    else:
        print(f"❌ Config failed: {response.text}")

def test_sse_events():
    """Test Server-Sent Events"""
    print("\n📡 Testing real-time events...")
    print("   (Start a scan in another terminal to see events)")
    print("   Press Ctrl+C to stop\n")
    
    # Get the latest task
    response = requests.get(f"{API_BASE}/api/tasks")
    tasks = response.json()["tasks"]
    
    if not tasks:
        print("❌ No tasks found. Run a scan first.")
        return
        
    latest_task = tasks[-1]
    task_id = latest_task["task_id"]
    
    print(f"Monitoring task: {task_id}")
    
    try:
        # Stream events
        response = requests.get(f"{API_BASE}/api/events/{task_id}", stream=True)
        
        for line in response.iter_lines():
            if line:
                if line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    print(f"📨 Event: {data['status']} - {data['progress']*100:.1f}% - {data['message']}")
                    
                    if data["status"] in ["completed", "failed"]:
                        break
    except KeyboardInterrupt:
        print("\n✅ Event streaming stopped")

def main():
    """Run all tests"""
    print("🧪 File Organizer API Test Suite")
    print("=" * 50)
    print(f"Testing API at: {API_BASE}")
    print("=" * 50)
    
    # Check if API is running
    try:
        requests.get(f"{API_BASE}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ API is not running!")
        print("   Start it with: python api.py")
        sys.exit(1)
    
    # Run tests
    test_health()
    test_config()
    
    # Get test path
    test_path = "."
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
    elif Path("test_folder").exists():
        test_path = "test_folder"
    
    print(f"\n📁 Using test path: {test_path}\n")
    
    # Test scan
    task_id = test_scan(test_path)
    
    if task_id:
        # Test prompt generation
        test_prompt_generation(test_path)
    
    # Test plan validation
    test_plan_validation()
    
    # Optional: Test SSE
    if input("\n🔔 Test real-time events? (y/N): ").lower() == 'y':
        test_sse_events()
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    main()