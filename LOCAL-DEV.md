# Local Development Setup

This guide shows how to run the Workflow Builder application with **PostgreSQL in Docker** and **frontend/backend running locally** in separate terminals.

## Prerequisites

- **Docker** (for PostgreSQL database)
- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Git** (for cloning)

## Quick Start

### 1. Start Database (Terminal 1)
```bash
./scripts/dev-db.sh
```
This will:
- Start PostgreSQL in Docker on port 5432
- Run database migrations
- Seed with sample data
- Keep running until you stop it

### 2. Start Backend (Terminal 2)
```bash
./scripts/dev-backend.sh
```
This will:
- Create Python virtual environment (first time)
- Install Python dependencies
- Connect to Docker PostgreSQL
- Start FastAPI server on http://localhost:8080

### 3. Start Frontend (Terminal 3)
```bash
./scripts/dev-frontend.sh
```
This will:
- Install Node.js dependencies (first time)
- Start Vite dev server on http://localhost:3000
- Connect to local backend

## What You Get

- **Frontend**: http://localhost:3000 (React + Vite with hot reload)
- **Backend API**: http://localhost:8080 (FastAPI with auto-reload)
- **API Docs**: http://localhost:8080/docs (Interactive Swagger docs)
- **Database**: PostgreSQL in Docker (persisted data)

## Demo Credentials

- **Email**: `demo@example.com`
- **Password**: `demo123`

## Development Workflow

### Daily Development
1. Start database: `./scripts/dev-db.sh` (leave running)
2. Start backend: `./scripts/dev-backend.sh` (leave running)
3. Start frontend: `./scripts/dev-frontend.sh` (leave running)
4. Code changes will auto-reload in both frontend and backend

### Stopping Services
- **Frontend/Backend**: Press `Ctrl+C` in respective terminals
- **Database**: `docker-compose stop postgres` or `Ctrl+C` in database terminal

### Resetting Database
```bash
docker-compose down -v     # Removes all data
./scripts/dev-db.sh       # Recreates with fresh data
```

## File Structure

```
/
├── scripts/
│   ├── dev-db.sh         # Start PostgreSQL in Docker
│   ├── dev-backend.sh    # Start FastAPI backend locally
│   ├── dev-frontend.sh   # Start React frontend locally
│   ├── setup.sh          # Original Docker setup
│   ├── run.sh            # Original Docker run
│   └── test.sh           # Test suite
├── backend/
│   ├── venv/         # Python virtual environment (auto-created)
│   ├── app/          # FastAPI application
│   └── requirements.txt
└── frontend/
    ├── node_modules/ # Node dependencies (auto-created)
    ├── src/          # React application
    └── package.json
```

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is running: `./scripts/dev-db.sh`
- Check Python version: `python --version` (needs 3.8+)
- Check database connection: `docker-compose ps`

### Frontend won't start
- Check Node.js version: `node --version` (needs 18+)
- Clear cache: `cd frontend && rm -rf node_modules && npm install`
- Check if backend is running: `curl http://localhost:8080/health`

### Database issues
- Reset database: `docker-compose down -v && ./scripts/dev-db.sh`
- Check logs: `docker-compose logs postgres`
- Manual connection test: `docker-compose exec postgres psql -U postgres workflow_builder`

### Port conflicts
- **3000** (frontend): Change in `frontend/vite.config.ts`
- **8080** (backend): Change in `dev-backend.sh` uvicorn command
- **5432** (database): Change in `docker-compose.yml`

## Benefits of This Setup

✅ **Fast Development**: Hot reload for both frontend and backend  
✅ **Easy Debugging**: Direct access to logs and debugger  
✅ **Flexible**: Can restart individual services  
✅ **IDE Friendly**: Better code completion and debugging  
✅ **Resource Efficient**: Only database runs in Docker  

## Switching Back to Full Docker

To use the original Docker setup:
```bash
docker-compose down    # Stop any running services
./scripts/setup.sh     # Original Docker setup
./scripts/run.sh       # Original Docker run
```

## Environment Variables

The scripts automatically set these for local development:

**Backend**:
- `DATABASE_URL`: `postgresql://postgres:postgres@localhost:5432/workflow_builder`
- `JWT_SECRET`: `dev-secret-key-change-in-production`

**Frontend**:
- `VITE_API_URL`: `http://localhost:8080`
