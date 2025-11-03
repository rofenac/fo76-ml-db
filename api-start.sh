#!/bin/bash

# Fallout 76 Build Database - API Server Startup Script

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Warning: Virtual environment not found at .venv"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Database credentials may not be configured."
fi

# Check if required dependencies are installed
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "FastAPI not installed. Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the API server
echo "Starting Fallout 76 Build Database API Server..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000
