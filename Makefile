# Makefile for HunterTeck

.PHONY: help setup dev install install-dev clean lint format test run docker-build docker-up docker-down docs ci

help:
	@echo "HunterTeck - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Setup development environment"
	@echo "  make install        - Install dependencies"
	@echo "  make install-dev    - Install dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Run app in development"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start Docker containers"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make docs           - Build documentation"
	@echo "  make ci             - Run CI checks"

setup:
	@echo "🚀 Setting up development environment..."
	bash scripts/setup.sh

install:
	pip install -e ".[streamlit,groq]"

install-dev:
	pip install -e ".[dev,streamlit,groq]"

dev:
	@echo "🟢 Starting Streamlit app..."
	streamlit run app_hunter.py

lint:
	@echo "🔍 Running linting checks..."
	flake8 services/ backend/ app_hunter.py orquestrador.py
	@echo "✅ Linting passed"

format:
	@echo "🎨 Formatting code..."
	black services/ backend/ app_hunter.py orquestrador.py
	isort services/ backend/ app_hunter.py orquestrador.py
	@echo "✅ Code formatted"

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --tb=short

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=services --cov=backend --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report: htmlcov/index.html"

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info htmlcov/ .pytest_cache/ .coverage
	@echo "✅ Cleaned"

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build
	@echo "✅ Build complete"

docker-up:
	@echo "🟢 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Services running"
	@echo "📊 Frontend: http://localhost:8501"

docker-down:
	@echo "🔴 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Stopped"

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

docs:
	@echo "📚 Building documentation..."
	@echo "See docs/README.md for documentation index"
	@echo "✅ Ready"

ci:
	@echo "🔄 Running CI checks..."
	bash scripts/check-quality.sh
	make test
	@echo "✅ All CI checks passed"

freeze:
	@echo "❄️  Freezing dependencies..."
	pip freeze > requirements-lock.txt
	@echo "✅ Frozen to requirements-lock.txt"

venv:
	@echo "🐍 Creating virtual environment..."
	python3 -m venv venv
	@echo "✅ Activate with: source venv/bin/activate"

.DEFAULT_GOAL := help
