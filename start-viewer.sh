#!/bin/bash
echo "Starting Excalidraw Auto Viewer..."

# Start file list generator in background
node generate-file-list.js --watch &
FILE_WATCHER_PID=$!

# Start HTTP server in background
http-server -p 8080 -c-1 &
HTTP_SERVER_PID=$!

# Open browser
sleep 2
open http://localhost:8080/excalidraw-viewer.html

echo "✓ File watcher running (PID: $FILE_WATCHER_PID)"
echo "✓ Server running at http://localhost:8080"
echo "✓ Browser opened"
echo ""
echo "Press Ctrl+C to stop"

# Wait and cleanup on exit
trap "kill $FILE_WATCHER_PID $HTTP_SERVER_PID" EXIT
wait
