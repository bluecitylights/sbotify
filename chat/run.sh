#!/bin/bash

echo "--- Contents of /app ---"
ls -la /app/.venv/bin/uvicorn
ls -la /app/.venv/bin/
ls -la /app/
ls -la /app/src/
echo "------------------------"


/app/.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}