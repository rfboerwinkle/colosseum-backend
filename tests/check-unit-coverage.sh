#!/bin/bash
set -euxo pipefail

source .venv/bin/activate
PYTHONPATH=. pytest -s tests/unit_tests/main.py --cov-report=html \
  --cov=party \
  --cov=api
