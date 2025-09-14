#!/bin/bash

echo "--- Contents of /app ---"
ls -la /app/.venv/bin/uvicorn
ls -la /app/.venv/bin/
ls -la /app/
echo "------------------------"


/app/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port ${PORT}