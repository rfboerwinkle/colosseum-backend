#!/bin/bash
# Should only be ran locally while server running
source tests/.venv/bin/activate
pytest tests/acceptance_tests/main.py
