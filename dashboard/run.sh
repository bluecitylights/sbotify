#!/bin/bash
/app/.venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT}