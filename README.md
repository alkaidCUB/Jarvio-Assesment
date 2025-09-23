# Workflow Builder - Take-Home Interview Project

A comprehensive full-stack application demonstrating a workflow builder similar to n8n, built for take-home interview assessments.

## 🏗️ Architecture

### Frontend
- **React 18** with **TypeScript** (strict mode)
- **Vite** for fast development and building
- **React Router** for navigation
- **Zustand** for state management
- **React Query** + **Axios** for data fetching
- **Tailwind CSS** for styling
- **React Hook Form** + **Zod** for form handling
- **ReactFlow** for workflow canvas
- **Lucide React** for icons

### Backend
- **FastAPI** with **Python 3.11**
- **SQLAlchemy** ORM with **Alembic** migrations
- **PostgreSQL 16** database
- **JWT** authentication (mock implementation)
- **Pydantic** for data validation
- **Docker** containerization
- **Gunicorn + Uvicorn** for production serving

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)

### Three Simple Commands

| Command | Purpose | Description |
|---------|---------|-------------|
| `./scripts/setup.sh` | **Setup** | Initialize database, install dependencies, build images |
| `./scripts/run.sh` | **Run** | Start all services (frontend, backend, database) |
| `./scripts/test.sh` | **Test** | Run comprehensive test suite with quality checks |

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

### Demo Credentials
- **Email**: `demo@example.com`
- **Password**: `demo123`

## 🛠️ Features

### Workflow Builder
The application includes a visual workflow builder with three types of nodes:

1. **Get Best Selling ASINs**
   - Fetches top N products by sales amount
   - Configurable count parameter
   - Returns list of ASINs

2. **Get ASIN by Index**
   - Selects a specific ASIN from a list by index
   - Configurable index parameter
   - Takes ASIN list as input, returns single ASIN

3. **Get ASIN Details**
   - Fetches detailed information for a single ASIN
   - Returns title, description, and bullet points
   - Takes single ASIN as input

## 📸 Screenshots

### Workflow Builder in Action
![Workflow Editor](images/example-workflow.png)
*Visual workflow designer showing a sequential product analysis workflow with three connected nodes: Get Best Selling ASINs → Get ASIN by Index → Get ASIN Details*

### Main Dashboard
![Dashboard](images/landing-page.png)
*Dashboard showing what workflows are in the application*

### Product Catalog
![My Products](images/my-products-page.png)
*Comprehensive product table with product attributes*

### Core Functionality
- **Visual Workflow Designer**: Drag-and-drop interface using ReactFlow
- **Workflow Execution**: Run workflows and view results
- **Result Persistence**: All workflow runs are stored and accessible
- **Authentication**: JWT-based auth with mock implementation
- **Real-time Updates**: Live workflow execution results

### Sample Data
The application comes pre-seeded with:
- 5 sample Amazon products with realistic data
- 1 example workflow demonstrating all three node types
- 1 sample workflow run with results

## 🏃‍♂️ Development

### Local Development Setup

1. **Backend Development**:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python seed_data.py
uvicorn app.main:app --reload --port 8080
```

2. **Frontend Development**:
```bash
cd frontend
npm install
npm run dev
```

### Database Management

**Create Migration**:
```bash
docker-compose exec backend alembic revision --autogenerate -m "Migration message"
```

**Apply Migrations**:
```bash
docker-compose exec backend alembic upgrade head
```

**Seed Data**:
```bash
docker-compose exec backend python seed_data.py
```

### Testing

#### **Running All Tests**

**Quick Test Suite** (Recommended):
```bash
# Run comprehensive test suite with one command
./scripts/test.sh
```

**Manual Test Commands**:
```bash
# Run individual test suites
docker-compose exec -T backend pytest -v          # Backend tests
docker-compose exec -T frontend npm run build     # Frontend build test
```

**Individual Test Commands**:

#### **Backend Tests**

**Run Tests**:
```bash
# Via Docker (recommended)
docker-compose exec -T backend pytest -v

# Or locally (requires Python environment)
cd backend
pytest -v
```

**Test Structure**:
- **Location**: `backend/tests/`
- **Framework**: pytest with FastAPI TestClient
- **Coverage**: API endpoints, authentication, basic functionality
- **Database**: Uses in-memory testing (no external DB required)

**Add New Tests**:
```bash
# Create new test file
touch backend/tests/test_workflows.py

# Example test structure:
def test_workflow_creation():
    response = client.post("/workflows/", json={
        "name": "Test Workflow",
        "description": "Test description",
        "flow_data": {"nodes": [], "edges": []}
    })
    assert response.status_code == 200
```

#### **Frontend Tests**

**Type Checking & Build Tests**:
```bash
# Via Docker
docker-compose exec -T frontend npm run build

# Via Docker - Type check only
docker-compose exec -T frontend npx tsc --noEmit

# Or locally
cd frontend
npm run build
```

**Linting**:
```bash
# Via Docker
docker-compose exec -T frontend npm run lint

# Or locally  
cd frontend
npm run lint
```

**Add Component Tests** (Future Enhancement):
```bash
# Install testing framework
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Add to package.json scripts:
# "test": "vitest"
```

#### **Backend Code Quality**

**Linting and Formatting**:
```bash
# Via Docker
docker-compose exec -T backend black app/
docker-compose exec -T backend isort app/ 
docker-compose exec -T backend flake8 app/

# Or locally
cd backend
black .
isort .
flake8 .
```

**Pre-commit Hooks** (Local Development):
```bash
cd backend
pre-commit install
pre-commit run --all-files
```

#### **Integration Tests**

**API Health Checks**:
```bash
# Test backend health
curl http://localhost:8080/health

# Test authentication
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "demo123"}'

# Test frontend is serving
curl http://localhost:3000
```

**Database Tests**:
```bash
# Check database connection
docker-compose exec -T backend python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection: OK')
"
```

#### **Creating New Tests**

**Backend Test Guidelines**:
1. **Location**: Add tests to `backend/tests/test_*.py`
2. **Naming**: Use descriptive names like `test_workflow_crud_operations`
3. **Structure**: Use FastAPI TestClient for API testing
4. **Database**: Tests use in-memory SQLite (no cleanup needed)

**Example Backend Test**:
```python
def test_create_workflow():
    response = client.post("/workflows/", json={
        "name": "Test Workflow", 
        "description": "Test",
        "flow_data": {"nodes": [], "edges": []}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workflow"
```

**Frontend Test Guidelines** (Future):
1. **Framework**: Vitest + Testing Library recommended
2. **Location**: Add tests to `frontend/src/**/*.test.tsx`
3. **Focus**: Component rendering, user interactions, API integration

#### **Continuous Integration**

**Test Pipeline Commands**:
```bash
# Complete test suite for CI/CD
./scripts/setup.sh                            # Setup application
docker-compose exec -T backend pytest -v     # Backend tests
docker-compose exec -T frontend npm run build # Frontend build test
docker-compose exec -T backend flake8 app/   # Linting
docker-compose down                           # Cleanup
```

**Test Environment Variables**:
```bash
# Add to .env for testing
DATABASE_URL=sqlite:///./test.db
JWT_SECRET=test-secret-key
```

## 📁 Project Structure

```
workflow-builder/
├── scripts/                  # Development and setup scripts
│   ├── setup.sh             # Docker setup script
│   ├── run.sh               # Docker run script
│   ├── test.sh              # Test suite script
│   ├── dev-db.sh            # Local dev: database only
│   ├── dev-backend.sh       # Local dev: backend only
│   └── dev-frontend.sh      # Local dev: frontend only
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── stores/          # Zustand stores
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── routers/         # API route handlers
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # Authentication logic
│   │   ├── database.py      # Database configuration
│   │   ├── config.py        # Application settings
│   │   └── workflow_engine.py # Workflow execution engine
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test files
│   └── requirements.txt
├── docker-compose.yml        # Docker services configuration
├── LOCAL-DEV.md             # Local development guide
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create `.env` files based on the `.env.example` template:

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflow_builder
JWT_SECRET=your-secret-key
AWS_ACCESS_KEY_ID=your-aws-key (optional)
AWS_SECRET_ACCESS_KEY=your-aws-secret (optional)
SLACK_WEBHOOK_URL=your-slack-webhook (optional)
```

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8080
```

## 🚀 Production Deployment

The application is containerized and production-ready:

1. **Backend**: Uses Gunicorn + Uvicorn for optimal performance
2. **Frontend**: Builds optimized static assets
3. **Database**: PostgreSQL 16 with proper migrations
4. **CORS**: Configured for cross-origin requests

### Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 🧪 Key Technical Decisions

### Authentication Strategy
- **Mock JWT Implementation**: Perfect for isolated local development
- **No External Dependencies**: Eliminates AWS Cognito setup complexity
- **Realistic Flow**: Maintains production-like authentication patterns

### State Management
- **Zustand**: Lightweight, TypeScript-friendly alternative to Redux
- **React Query**: Handles server state with caching and synchronization
- **Persistent Storage**: Auth state persists across browser sessions

### Workflow Engine
- **Simple Topological Sort**: Determines node execution order
- **Result Chaining**: Passes data between connected nodes
- **Error Handling**: Graceful failure with detailed error messages

### Database Design
- **Normalized Schema**: Separate tables for users, workflows, runs, and products
- **JSON Storage**: Flexible workflow definition storage
- **UUID Primary Keys**: Better for distributed systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper tests
4. Run pre-commit hooks
5. Submit a pull request

## 📋 Interview Assessment Criteria

This project demonstrates:

✅ **Full-Stack Proficiency**: React + FastAPI integration  
✅ **Modern Tooling**: Vite, TypeScript strict mode, React Query  
✅ **Database Skills**: SQLAlchemy, Alembic migrations, PostgreSQL  
✅ **Authentication**: JWT implementation and protected routes  
✅ **UI/UX**: Interactive workflow builder with ReactFlow  
✅ **Testing**: Backend tests with pytest  
✅ **DevOps**: Docker containerization and development setup  
✅ **Code Quality**: Pre-commit hooks, linting, formatting  
✅ **Documentation**: Comprehensive setup and usage instructions  
✅ **Architecture**: Clean separation of concerns and scalable structure

## 🛑 Stopping the Application

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

---

**Built with ❤️ for take-home interview assessments**# fullstack-interview-example
