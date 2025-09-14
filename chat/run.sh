#!/bin/bash

echo "--- Contents of /app ---"
ls -la /app/.venv/bin/bin/
echo "------------------------"


/app/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port ${PORT}