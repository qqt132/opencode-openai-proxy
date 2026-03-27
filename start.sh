#!/bin/bash
# OpenCode OpenAI Proxy Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting OpenCode OpenAI Proxy..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed. Please run:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Start the proxy
echo "✓ Starting proxy on http://localhost:8000"
echo "✓ Logs: $SCRIPT_DIR/proxy.log"
echo ""

# Run in foreground (use nohup for background)
python opencode_openai_proxy_v2.py

# For background mode, uncomment:
# nohup python opencode_openai_proxy_v2.py > proxy.log 2>&1 &
# echo "✓ Proxy started in background (PID: $!)"
# echo "  View logs: tail -f proxy.log"
