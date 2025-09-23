#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.."

echo "🐍 Starting Backend for Local Development..."

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if Docker PostgreSQL is running with our database
echo "🔍 Checking Docker PostgreSQL..."
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ Docker PostgreSQL is not running"
    echo "💡 Make sure to run: ./scripts/dev-db.sh first"
    exit 1
fi

# Simple connection test
echo "🔍 Testing database connection..."
if ! docker-compose exec -T postgres psql -U postgres workflow_builder -c "SELECT COUNT(*) FROM my_products;" >/dev/null 2>&1; then
    echo "❌ Cannot connect to database or demo data missing"
    echo "💡 Make sure to run: ./scripts/dev-db.sh first"
    exit 1
fi

echo "✅ Database connection verified"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    # Use Python 3.11 for compatibility with packages like psycopg2-binary and pydantic-core
    if command -v python3.11 &> /dev/null; then
        echo "📦 Using Python 3.11 for better package compatibility..."
        python3.11 -m venv venv
    else
        echo "📦 Using default Python 3..."
        python3 -m venv venv
    fi
    cd ..
fi

# Navigate to backend directory and activate virtual environment
cd backend
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Verify virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install dependencies if needed
if [ ! -f "venv/requirements_installed.flag" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/requirements_installed.flag
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "📦 Dependencies already installed"
fi

# Set environment variables for local development
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/workflow_builder"
export JWT_SECRET="dev-secret-key-change-in-production"

# Verify critical dependencies are available (only if flag file doesn't exist)
if [ ! -f "venv/requirements_installed.flag" ]; then
    echo "🔍 Verifying dependencies..."
    python -c "import fastapi, uvicorn, sqlalchemy, psycopg2" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ Critical dependencies missing after installation"
        exit 1
    fi
    touch venv/requirements_installed.flag
    echo "✅ Dependencies verified and flagged"
fi

echo ""
echo "✅ Backend setup complete!"
echo "🚀 Starting FastAPI server on http://localhost:8080"
echo "📚 API Documentation: http://localhost:8080/docs"
echo ""
echo "💡 Demo credentials:"
echo "   Email: demo@example.com"
echo "   Password: demo123"
echo ""
echo "📋 Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
