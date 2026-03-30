#!/bin/bash

# Fallout 76 Build Database - API Server Startup Script

# Ensure dependencies are up to date
uv sync

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Database credentials may not be configured."
fi

# Start the API server
echo "Starting Fallout 76 Build Database API Server..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
