#!/bin/bash

echo "--- Contents of /app ---"
ls -l /app
echo "------------------------"

/app/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port ${PORT}