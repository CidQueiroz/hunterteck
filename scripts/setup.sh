#!/bin/bash
# Setup development environment

set -e

echo "🚀 Setting up HunterTeck development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded"

# Install dependencies
echo "📚 Installing dependencies..."
pip install -e ".[dev,streamlit,groq]"
echo "✓ Dependencies installed"

# Setup pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "🔧 Setting up pre-commit hooks..."
    pre-commit install
else
    echo "⚠️  pre-commit not found, skipping hooks"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create logs directory if it doesn't exist
mkdir -p logs data/backups
echo "📁 Created log and data directories"

# Run tests
echo "🧪 Running basic tests..."
python -m pytest tests/ -v --tb=short || echo "⚠️  Some tests failed"

echo "\n✅ Development environment setup complete!"
echo "\n📖 Next steps:"
echo "1. Edit .env with your API keys:"
echo "   nano .env"
echo "\n2. Run the Streamlit app:"
echo "   streamlit run app_hunter.py"
echo "\n3. Or run tests:"
echo "   pytest"
