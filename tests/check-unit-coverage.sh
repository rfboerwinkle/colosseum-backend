#!/bin/bash
source tests/.venv/bin/activate
pytest tests/unit_tests/main.py \
  --cov=src \
  --cov-report=term \
  --cov-report=html
