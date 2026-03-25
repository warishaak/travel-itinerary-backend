#!/bin/bash
# Pre-push setup script - installs pre-commit hooks and dependencies

echo "🔧 Setting up pre-push hooks..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv || { echo "❌ Failed to create virtual environment"; exit 1; }
    echo "✓ Virtual environment created"
fi

# Setup Python path
VENV_BIN=".venv/bin"
if [ ! -f "$VENV_BIN/python" ]; then
    echo "❌ Virtual environment not properly created"
    exit 1
fi

# Install/upgrade pip
echo "📚 Upgrading pip..."
"$VENV_BIN/pip" install --upgrade pip || { echo "❌ Failed to upgrade pip"; exit 1; }

# Install dependencies
echo "📦 Installing project dependencies..."
"$VENV_BIN/pip" install -r requirements.txt || { echo "❌ Failed to install dependencies"; exit 1; }

# Install pre-commit
echo "🔐 Installing pre-commit framework..."
"$VENV_BIN/pip" install pre-commit || { echo "❌ Failed to install pre-commit"; exit 1; }

# Install pre-commit hooks
echo "🪝 Installing git hooks..."
"$VENV_BIN/pre-commit" install || { echo "❌ Failed to install git hooks"; exit 1; }

