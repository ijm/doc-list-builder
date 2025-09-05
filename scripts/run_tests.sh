#!/bin/bash
# Boilerplate for running tests and linters

# Exit on error
set -e

# Run tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run linters
echo "\nRunning flake8..."
python -m flake8 src/

echo "\nRunning pylint..."
python -m pylint src/
