#!/bin/bash
# Unix/Linux shell script for running agent tests
# Agent Test Framework V3.6.9

set -e  # Exit on error

echo
echo "================================================================"
echo "   AGENT TEST FRAMEWORK V3.6.9"
echo "   Comprehensive Testing for all 37 Agents"
echo "================================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.9+ and add to PATH"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "test-runner.py" ]; then
    echo "❌ Please run this script from the tests/ directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Setup environment if needed
mkdir -p logs reports data baselines temp

echo "🔧 Setting up test environment..."

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    python3 -m pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  No requirements.txt found, skipping dependency installation"
fi

echo
echo "🚀 Starting comprehensive agent testing..."
echo

# Default to running all tests unless arguments provided
if [ $# -eq 0 ]; then
    echo "Running all test suites..."
    python3 test-runner.py --verbose
else
    echo "Running with custom arguments: $*"
    python3 test-runner.py "$@"
fi

TEST_EXIT_CODE=$?

echo
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Tests completed successfully!"
    echo
    echo "📊 Check results in:"
    echo "  - HTML Report: reports/test-report-*.html"
    echo "  - JSON Results: reports/test-results-*.json"
    echo "  - Logs: logs/agent-test-execution.log"
else
    echo "❌ Tests failed with exit code $TEST_EXIT_CODE"
    echo
    echo "🔍 Check logs for details:"
    echo "  - Logs: logs/agent-test-execution.log"
    echo "  - Reports: reports/"
fi

echo
echo "================================================================"
echo "   For help: python3 test-runner.py --help"
echo "   Documentation: README.md"
echo "================================================================"

exit $TEST_EXIT_CODE