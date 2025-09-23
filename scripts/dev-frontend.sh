#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.."

echo "⚛️  Starting Frontend for Local Development..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "⚠️  Backend doesn't seem to be running on http://localhost:8080"
    echo "💡 Make sure to run: ./scripts/dev-backend.sh in another terminal"
    echo "🔄 Continuing anyway - you can start the backend later"
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Set environment variables for local development
export VITE_API_URL=http://localhost:8080

echo ""
echo "✅ Frontend setup complete!"
echo "🚀 Starting Vite development server on http://localhost:3000"
echo ""
echo "💡 Demo credentials:"
echo "   Email: demo@example.com"
echo "   Password: demo123"
echo ""
echo "📋 Press Ctrl+C to stop the server"
echo ""

# Start the Vite development server
npm run dev
