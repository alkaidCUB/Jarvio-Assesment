#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.."

echo "🐘 Starting PostgreSQL Database for Local Development..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start only the PostgreSQL service
echo "🔧 Starting PostgreSQL service..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; do
    echo "   Still waiting for PostgreSQL..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Start backend service temporarily for database operations
echo "🔧 Starting backend service for database setup..."
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Run database migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic revision --autogenerate -m "Initial migration" 2>/dev/null || echo "Migration generation skipped"
docker-compose exec -T backend alembic upgrade head || echo "⚠️  Migration failed"

# Create tables directly if migrations failed
echo "📊 Ensuring database tables exist..."
docker-compose exec -T backend python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Tables created/verified successfully!')
" || echo "⚠️  Table creation failed"

# Seed the database
echo "🌱 Seeding database with sample data..."
docker-compose exec -T backend python seed_data.py || echo "⚠️  Database seeding failed"

# Stop backend service (keep only postgres for local development)
echo "🔧 Stopping backend service (keeping only PostgreSQL for local development)..."
docker-compose stop backend

echo ""
echo "✅ Database setup complete!"
echo "🔗 PostgreSQL Connection: postgresql://postgres:postgres@localhost:5432/workflow_builder"
echo ""
echo "📋 To stop the database, run: docker-compose stop postgres"
echo "📋 To remove database data, run: docker-compose down -v"
