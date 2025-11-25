# Docker Guide for Airport Asset Management API

## What is Docker?

Docker is a platform that packages your application and all its dependencies into a **container** - a lightweight, portable environment that runs the same way everywhere.

### The Problem Docker Solves

**Without Docker:**
- "It works on my machine" - different environments cause issues
- Complex setup instructions
- Version conflicts between projects
- Hard to deploy to production

**With Docker:**
- "It works everywhere" - same environment on all machines
- One command to run everything
- Isolated environments (no conflicts)
- Easy deployment

## Why Use Docker for This Project?

### 1. **Easy Setup for New Developers**

**Without Docker:**
```bash
# New developer needs to:
1. Install Python 3.10+
2. Install PostgreSQL
3. Create virtual environment
4. Install dependencies
5. Configure .env file
6. Set up database
7. Run seed script
# ... many steps, potential errors
```

**With Docker:**
```bash
# New developer just needs:
docker-compose up
# Everything runs automatically!
```

### 2. **Consistent Environment**

- Same Python version everywhere
- Same PostgreSQL version
- Same dependencies
- No "works on my machine" issues

### 3. **Easy Deployment**

- Deploy to any server (AWS, Azure, DigitalOcean)
- Same container works everywhere
- No need to configure server manually

### 4. **Isolation**

- Your project's dependencies don't conflict with other projects
- Clean environment every time
- Easy to reset if something breaks

### 5. **Production Ready**

- Same container used in development and production
- Reduces deployment issues
- Industry standard for modern applications

## Docker Concepts

### Container
A lightweight, isolated environment that runs your application.

### Image
A template/blueprint for creating containers. Like a class in programming.

### Dockerfile
Instructions for building an image (like a recipe).

### Docker Compose
Tool for running multiple containers together (API + Database).

## How It Would Work for Your Project

### Current Setup (Without Docker)

```
Your Computer
├── Python 3.14
├── PostgreSQL (running separately)
├── Virtual environment (.venv)
└── Your code
```

**Problems:**
- Need to install PostgreSQL separately
- Need to configure database connection
- Different versions on different machines
- Hard to share with team

### With Docker

```
Docker Container 1 (API)
├── Python 3.10
├── All dependencies
└── Your code

Docker Container 2 (PostgreSQL)
├── PostgreSQL 15
└── Database data

Both containers talk to each other
```

**Benefits:**
- Everything packaged together
- One command to start everything
- Same on all machines
- Easy to share

## Example: Docker Setup for Your Project

### 1. Dockerfile (For Your API)

```dockerfile
# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. docker-compose.yml (For API + Database)

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: airport_user
      POSTGRES_PASSWORD: airport_password
      POSTGRES_DB: airport_assets
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airport_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Application
  api:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://airport_user:airport_password@db:5432/airport_assets
      ENVIRONMENT: development
      DEBUG: "true"
      SECRET_KEY: your-secret-key-here
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
    depends_on:
      db:
        condition: service_healthy
```

### 3. .dockerignore (Exclude unnecessary files)

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
venv/
.env
.git
.gitignore
*.md
.pytest_cache
.coverage
```

## How to Use

### Start Everything

```bash
docker-compose up
```

This will:
1. Build your API container
2. Start PostgreSQL container
3. Connect them together
4. Run your API

### Access Your API

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Database: localhost:5432

### Stop Everything

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f
```

### Run Commands in Container

```bash
# Run seed script
docker-compose exec api python scripts/seed_admin.py

# Run tests
docker-compose exec api pytest

# Access database
docker-compose exec db psql -U airport_user -d airport_assets
```

## Benefits for Your Specific Project

### 1. **Team Collaboration**

Everyone on your team:
- Gets the same environment
- No setup headaches
- Can start working immediately

### 2. **CI/CD Pipeline**

Easy to integrate with:
- GitHub Actions
- Azure DevOps
- AWS CodePipeline

### 3. **Deployment**

Deploy to:
- Azure Container Instances
- AWS ECS/Fargate
- Kubernetes
- Any cloud provider

### 4. **Testing**

- Clean environment for each test run
- No database setup needed
- Consistent test results

## When to Use Docker

### ✅ Good For:
- Team projects
- Production deployments
- CI/CD pipelines
- Complex dependencies
- Multi-service applications

### ❌ Maybe Not Needed For:
- Simple personal projects
- Learning projects (unless learning Docker)
- Projects with no external dependencies

## For Your Project

**Recommendation: YES, use Docker!**

Your project has:
- ✅ Multiple services (API + Database)
- ✅ External dependencies (PostgreSQL)
- ✅ Team collaboration potential
- ✅ Production deployment needs
- ✅ Complex setup requirements

Docker would make your project:
- Easier to set up
- More professional
- Production-ready
- Easier to deploy
- Better for team collaboration

## Next Steps

If you want to add Docker to your project:

1. Create `Dockerfile` (for API)
2. Create `docker-compose.yml` (for API + Database)
3. Create `.dockerignore`
4. Update `.env` for Docker environment
5. Test locally with `docker-compose up`

This would be especially valuable since your original plan mentioned:
- Containerization & Orchestration (Phase 3)
- Cloud deployment (Azure)
- Docker/Kubernetes

Docker is the foundation for all of these!

