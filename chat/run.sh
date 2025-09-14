#!/bin/bash

/app/.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}