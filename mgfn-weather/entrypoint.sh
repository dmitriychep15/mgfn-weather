#!/bin/bash

export PYTHONPATH=.

source .venv/bin/activate &&

# Let the DB start
python backend_pre_start.py &&

# Run migrations
alembic upgrade head &&

# Run FastAPI application
uvicorn src.main:app --host 0.0.0.0 --port 5000
