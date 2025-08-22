#!/bin/bash

echo "================================================================================"
echo "                    Claude Code Dev Stack v3.6.9"
echo "                   Complete NGROK Integration Startup"
echo "================================================================================"

echo
echo "🚀 Starting complete NGROK integration with all services..."
echo

# Check if NGROK is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ NGROK is not installed or not in PATH"
    echo "Please install NGROK from: https://ngrok.com/download"
    exit 1
fi

echo "✅ NGROK found in PATH"

# Check for auth token
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "⚠️  NGROK_AUTHTOKEN environment variable not set"
    echo "Please set your NGROK auth token:"
    echo "    export NGROK_AUTHTOKEN=your_token_here"
    echo "Or add it to .env file in config/ngrok/ directory"
    echo
fi

echo
echo "📦 Starting services in order..."
echo

# Start all services using Node.js
echo "🔄 Starting all services with NGROK integration..."
node scripts/start-all-services.js

echo
echo "✅ Complete NGROK integration started!"
echo
echo "💡 Available Commands:"
echo "    node scripts/ngrok-manager.js start     - Start NGROK tunnels only"
echo "    node scripts/webhook-server.js         - Start webhook server only"
echo "    node scripts/ngrok-health-monitor.js   - Start health monitoring"
echo "    node bin/ngrok-cli.js status           - Check status"
echo "    node bin/ngrok-cli.js urls             - Show tunnel URLs"
echo
echo "🌐 Access Points:"
echo "    NGROK Dashboard: http://localhost:4040"
echo "    Web App:         http://localhost:3000"
echo "    API Server:      http://localhost:8000"
echo "    Webhook Server:  http://localhost:4000"
echo "    Terminal:        http://localhost:3003"
echo
echo "Press Ctrl+C to stop all services"

# Keep script running
read -p "Press Enter to stop all services..."