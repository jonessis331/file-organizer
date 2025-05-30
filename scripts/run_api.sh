#!/bin/bash

    # File Organizer API Startup Script

    echo "🚀 Starting File Organizer API..."

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt

    # Create necessary directories
    echo "📁 Creating directories..."
    mkdir -p data logs

    # Start the API
    echo "🚀 Starting FastAPI server..."
    echo "=================================================="
    echo "API will be available at: http://localhost:8765"
    echo "API Documentation: http://localhost:8765/docs"
    echo "=================================================="
    echo ""

    # Run the API with the new path
    cd backend && python -m api.main
    