#!/bin/bash
# Hook setup script - installs pre-commit + pre-push checks and dependencies.

set -euo pipefail

echo "Setting up git hooks for backend..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

VENV_BIN=".venv/bin"
if [ ! -f "$VENV_BIN/python" ]; then
    echo "Virtual environment was not created correctly."
    exit 1
fi

echo "Upgrading pip..."
"$VENV_BIN/pip" install --upgrade pip

echo "Installing backend dependencies..."
"$VENV_BIN/pip" install -r requirements.txt

echo "Installing pre-commit..."
"$VENV_BIN/pip" install pre-commit

echo "Installing pre-commit and pre-push hooks..."
"$VENV_BIN/pre-commit" install --hook-type pre-commit --hook-type pre-push

echo "Backend hook setup complete."
echo "Pre-push checks run: django check, migration check, and tests."

