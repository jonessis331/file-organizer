#!/bin/bash

    # Development mode with auto-reload

    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

    echo "🔄 Starting API in development mode with auto-reload..."
    cd backend && uvicorn api.main:app --reload --host 127.0.0.1 --port 8765
    