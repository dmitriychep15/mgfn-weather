#!/bin/bash

export PYTHONPATH=.

source .venv/bin/activate &&

# Run tests
pytest . --asyncio-mode=auto -v -s
