#!/bin/bash
# Claude Code Dev Stack v3.0 - Universal Setup Script
# This script sets up the complete development environment

echo "=========================================="
echo "🚀 Claude Code Dev Stack v3.0 Setup"
echo "=========================================="

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    OS="unknown"
fi

echo "📍 Detected OS: $OS"

# Check Python installation
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "🐍 Using Python: $PYTHON_CMD"

# Run Python setup script
echo "📦 Setting up virtual environment..."
$PYTHON_CMD setup_environment.py

# Check if venv was created successfully
if [ -d "venv" ]; then
    echo "✅ Virtual environment created"
    
    # Activate venv based on OS
    if [[ "$OS" == "windows" ]]; then
        echo "📌 To activate: activate.bat (CMD) or .\\activate.ps1 (PowerShell)"
    else
        echo "📌 Activating virtual environment..."
        source venv/bin/activate
        
        # Install Node dependencies for React PWA
        echo "📦 Installing Node.js dependencies..."
        cd apps/web
        npm install
        cd ../..
        
        # Install React Native dependencies
        echo "📦 Setting up React Native..."
        cd apps/mobile
        npm install
        cd ../..
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "📚 Next Steps:"
    echo "1. Activate virtual environment:"
    if [[ "$OS" == "windows" ]]; then
        echo "   CMD: activate.bat"
        echo "   PowerShell: .\\activate.ps1"
    else
        echo "   source activate.sh"
    fi
    echo ""
    echo "2. Start development:"
    echo "   PWA: cd apps/web && npm run dev"
    echo "   Mobile: cd apps/mobile && npm run start"
    echo ""
    echo "3. Run tests:"
    echo "   npm test"
    echo ""
    echo "📖 Documentation: docs/README.md"
    echo "🔧 Configuration: .env.example"
    echo ""
    echo "🙏 Attribution:"
    echo "   See CREDITS.md for all integrated projects"
    echo "=========================================="
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi