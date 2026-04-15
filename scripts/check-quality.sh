#!/bin/bash
# Run code quality checks

echo "🔍 Running code quality checks..."

echo "\n📋 Checking with black..."
black --check services/ backend/ app_hunter.py orquestrador.py

echo "\n📐 Checking with flake8..."
flake8 services/ backend/ app_hunter.py orquestrador.py

echo "\n🔬 Type checking with mypy..."
mypy services/ backend/ --ignore-missing-imports

echo "\n📦 Sorting imports with isort..."
isort --check-only services/ backend/ app_hunter.py orquestrador.py

echo "\n✅ All quality checks passed!"
