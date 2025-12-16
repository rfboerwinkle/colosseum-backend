#!/bin/bash
set -euxo pipefail

# Should only be ran locally while server running
source .venv/bin/activate
pytest tests/acceptance_tests/main.py
