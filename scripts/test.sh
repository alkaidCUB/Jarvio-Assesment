#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.."

echo "🧪 Running Workflow Builder Test Suite..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Function to run test and check result
run_test() {
    echo -e "${YELLOW}Running: $1${NC}"
    if eval "$1"; then
        print_status 0 "$2"
    else
        print_status 1 "$2"
        return 1
    fi
}

# Check if services are running
echo "🔍 Checking if services are running..."
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Services not running. Please run './scripts/run.sh' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services are running${NC}"
echo ""

# Backend Tests
echo "🐍 Backend Tests"
echo "=================="

# Python tests
run_test "docker-compose exec -T backend pytest -v --tb=short" "Python unit tests" || exit 1

# API health check  
run_test "curl -s http://localhost:8080/health | grep -q 'healthy'" "API health endpoint" || exit 1

# Authentication test
run_test "curl -s -X POST http://localhost:8080/auth/login -H 'Content-Type: application/json' -d '{\"email\": \"demo@example.com\", \"password\": \"demo123\"}' | grep -q 'access_token'" "Authentication endpoint" || exit 1

echo ""

# Frontend Tests  
echo "⚛️  Frontend Tests"
echo "=================="

# TypeScript compilation and build
run_test "docker-compose exec -T frontend npm run build > /dev/null 2>&1" "TypeScript compilation & build" || exit 1

# Frontend serving check
run_test "curl -s http://localhost:3000 | grep -qi 'doctype html'" "Frontend serving" || exit 1

echo ""

# Code Quality (optional - warnings don't fail)
echo "🔍 Code Quality Checks"
echo "====================="

echo -e "${YELLOW}Running: Backend linting (flake8)${NC}"
if docker-compose exec -T backend flake8 app/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend linting - no errors${NC}"
else
    echo -e "${YELLOW}⚠️  Backend linting - warnings found (non-critical)${NC}"
fi

echo ""

# Integration Tests
echo "🔗 Integration Tests"
echo "==================="

# Database connection test
run_test "docker-compose exec -T backend python -c 'from app.database import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text(\"SELECT 1\")); print(\"OK\")' | grep -q 'OK'" "Database connection" || exit 1

echo ""
echo -e "${GREEN}🎉 All critical tests passed!${NC}"
echo ""
echo "📊 Test Summary:"
echo "   ✅ Backend API endpoints working"
echo "   ✅ Authentication system working"  
echo "   ✅ Frontend builds and serves correctly"
echo "   ✅ Database connection established"
echo "   ✅ Docker services operational"
echo ""
echo "🚀 Application ready for demo!"