#!/usr/bin/env bash
# launch.sh — Start the full SAFER-VLA stack
#
# Usage:
#   ./launch.sh          # Start API + signaling
#   ./launch.sh --dev    # Development mode with auto-reload
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "═══════════════════════════════════════════════════"
echo "  SAFER-VLA — Starting Full Stack                 "
echo "═══════════════════════════════════════════════════"

# Check dependencies
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "[INSTALL] Installing dependencies..."
    pip install -r "$SCRIPT_DIR/server/requirements.txt"
fi

# Start signaling server (background)
echo ""
echo "[1/2] Starting WebRTC signaling server on :8765..."
python3 "$SCRIPT_DIR/server/signaling.py" --port 8765 &
SIGNAL_PID=$!
echo "  PID: $SIGNAL_PID"

# Wait for signaling to bind
sleep 1

# Start API server
echo ""
echo "[2/2] Starting FastAPI backend on :8000..."
if [[ "${1:-}" == "--dev" ]]; then
    echo "  Mode: development (auto-reload)"
    cd "$SCRIPT_DIR"
    uvicorn server.api:app --host 0.0.0.0 --port 8000 --reload &
else
    python3 "$SCRIPT_DIR/server/api.py" &
fi
API_PID=$!
echo "  PID: $API_PID"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  SAFER-VLA — RUNNING                             "
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Command Center:  http://localhost:8000"
echo "  API Docs:        http://localhost:8000/api/docs"
echo "  Fleet API:       http://localhost:8000/api/fleet"
echo "  Signaling:       ws://localhost:8765"
echo "  Health:          http://localhost:8000/api/health"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════"

# Trap and cleanup
trap "kill $SIGNAL_PID $API_PID 2>/dev/null; echo ''; echo 'Stopped.'" EXIT INT TERM

# Wait for any background process to exit
wait
