#!/bin/bash
set -e

# Default values
DEBUG_PORT=${DEBUG_PORT:-5678}
APP_PORT=${APP_PORT:-8000}
DEBUG_WAIT=${DEBUG_WAIT:-false}
DEBUG_MODE=${DEBUG_MODE:-false}

if [ "$DEBUG_MODE" = "true" ]; then
    echo "🐛 Starting FastAPI with debugger support..."
    echo "📍 Debug port: $DEBUG_PORT"
    echo "🌐 App port: $APP_PORT"
    echo "⏳ Wait for debugger: $DEBUG_WAIT"
    
    if [ "$DEBUG_WAIT" = "true" ]; then
        echo "⏳ Waiting for debugger to attach on port $DEBUG_PORT..."
        echo "🔗 Connect your debugger to localhost:$DEBUG_PORT"
        exec python -m debugpy --listen 0.0.0.0:$DEBUG_PORT --wait-for-client -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
    else
        echo "🚀 Starting with debugger listening (no wait)..."
        exec python -m debugpy --listen 0.0.0.0:$DEBUG_PORT -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
    fi
else
    echo "🚀 Starting FastAPI in normal mode..."
    exec uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
fi
