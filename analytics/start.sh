#!/bin/sh

# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 4004 &
BACKEND_PID=$!

# Start frontend
serve -s frontend/dist -l 4005 &
FRONTEND_PID=$!

# Wait for both
wait $BACKEND_PID $FRONTEND_PID
