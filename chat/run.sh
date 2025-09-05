#!/bin/bash
/app/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port ${PORT}