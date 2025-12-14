# Monday Merch - E-commerce API Assignment

## Task Overview

This project implements a RESTful API for an e-commerce platform as part of a coding assignment. The API provides product listing functionality with search, filtering, and pagination capabilities, along with JWT-based authentication to protect endpoints.

### Requirements

- Design and implement a relational database schema for an e-commerce system
- Create a product listing endpoint with:
  - Search functionality
  - Category filtering
  - Pagination
- Implement user authentication
- Follow clean architecture principles
- Provide proper documentation

## Implemented Solution

### Architecture

The solution follows a **Layered Architecture** pattern with strict separation of concerns:

- **Routers Layer**: Defines API endpoints and routes requests
- **Controllers Layer**: Handles HTTP orchestration and calls services
- **Services Layer**: Contains pure business logic and database queries
- **Models Layer**: SQLAlchemy domain models and Pydantic schemas

### Database Schema

The schema includes five main tables:

- **Users**: Customer information with authentication credentials
- **Categories**: Product categories (Electronics, Clothing, Books, etc.)
- **Products**: Product catalog with pricing and inventory
- **Orders**: Customer purchase orders
- **Order Items**: Line items within orders (with price snapshots)

### Features Implemented

1. **Product Listing API** (`GET /api/v1/products`)
   - Search products by title
   - Filter by category (dropdown in Swagger)
   - Pagination support
   - Protected endpoint (requires authentication)

2. **Authentication** (`POST /api/v1/auth/login`)
   - JWT-based authentication
   - Password hashing with bcrypt
   - Token expiration handling

3. **Health Check** (`GET /health`)
   - API health status
   - Database connectivity check
   - Returns 503 if database is unavailable

4. **Additional Features**
   - Automatic database seeding on startup
   - Comprehensive exception handling
   - Structured logging with loguru
   - Pre-commit hooks for code quality
   - Docker containerization with PostgreSQL

### Technical Stack

- **Framework**: FastAPI
- **Database**: SQLite (local dev) / PostgreSQL (Docker/production)
- **ORM**: SQLAlchemy (Async)
- **Validation**: Pydantic
- **Authentication**: JWT (python-jose) + bcrypt
- **Logging**: Loguru
- **Containerization**: Docker & Docker Compose

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for production setup)
- pip

### Local Development (SQLite)

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python -m app.main
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

4. **Test credentials:**
   The database is automatically seeded with the following test users:
   - Email: `test@example.com` / Password: `testpassword123`
   - Email: `john.doe@example.com` / Password: `password123`
   - Email: `jane.smith@example.com` / Password: `password123`

### Production Setup (Docker with PostgreSQL)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Build and start services:**
   ```bash
   docker-compose up --build
   ```

   Or run in detached mode:
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f api
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

5. **Clean restart (removes database):**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

### Using Makefile (Optional)

```bash
# Build containers
make build

# Start services
make up

# View logs
make logs

# Stop services
make down

# Restart services
make restart

# Clean restart (removes database volumes)
make clean

# Complete teardown (stops, removes containers, volumes, and images)
make teardown

# Single command: build, start, and show logs, up up and fly away!!
make fly
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Authenticate and get JWT token
  - Body: `{"email": "test@example.com", "password": "testpassword123"}`
  - Returns: `{"access_token": "...", "token_type": "bearer"}`

### Products (Protected)

- `GET /api/v1/products` - List products with filtering and pagination
  - Query Parameters:
    - `search` (optional): Search term for product title
    - `category` (optional): Filter by category (Electronics, Clothing, Books, etc.)
    - `page` (default: 1): Page number
    - `page_size` (default: 10, max: 100): Items per page
  - Headers: `Authorization: Bearer <token>`

### Health Check

- `GET /health` - Check API and database health
  - Returns 200 if healthy, 503 if database is unavailable

## Environment Variables

### Local Development

Create a `.env` file in the `backend/` directory (optional for local dev):

```bash
cp .env.example .env
# Edit .env with your values
```

Example `.env` file:
```env
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# For PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Application
DEBUG=false
APP_NAME=Monday Merch - Assignment E-commerce API

# Authentication
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Production Secret Management

**⚠️ IMPORTANT**: The current `docker-compose.yml` uses default values for local development. **These are NOT secure for production.**

For production deployments, see **[SECRETS.md](backend/SECRETS.md)** for comprehensive guidance on:
- Docker Secrets (Docker Swarm)
- External Secret Managers (AWS Secrets Manager, HashiCorp Vault, etc.)
- CI/CD Pipeline Secrets
- Best practices and security checklist

**Quick Production Setup**:
1. Copy `.env.example` to `.env` and set secure values
2. Generate strong secrets:
   ```bash
   # Generate SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Generate database password
   openssl rand -base64 32
   ```
3. Use environment variables or a secret manager (see `SECRETS.md` for details)
4. Never commit `.env` to version control (already in `.gitignore`)

For Docker, environment variables can be set in `docker-compose.yml` or passed via `.env` file.

## Database

### Local Development
- Uses SQLite (`app.db` file)
- Tables created automatically on startup
- Seed data populated if database is empty:
  - 5 product categories
  - 12 sample products
  - 3 test users with complete profile information

### Production (Docker)
- Uses PostgreSQL 15
- Persistent data in Docker volume
- Tables created automatically on startup
- Seed data populated if database is empty:
  - 5 product categories
  - 12 sample products
  - 3 test users with complete profile information

## Project Structure

```
backend/
├── app/
│   ├── api/              # API layer (routers, controllers, serializers)
│   ├── core/             # Configuration, database, security, logging
│   ├── models/           # SQLAlchemy domain models
│   ├── services/         # Business logic layer
│   ├── utils/            # Utilities (pagination, seeding)
│   └── main.py           # Application entry point
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker services orchestration (local dev)
├── docker-compose.prod.example.yml  # Production example
├── .env.example          # Environment variables template
├── SECRETS.md            # Secret management guide
├── requirements.txt      # Python dependencies
└── Makefile             # Convenience commands
```

## Testing the API

### 1. Get Authentication Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

### 2. Access Products Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/products?page=1&page_size=10" \
  -H "Authorization: Bearer <your-token-here>"
```

### 3. Search Products

```bash
curl -X GET "http://localhost:8000/api/v1/products?search=headphones" \
  -H "Authorization: Bearer <your-token-here>"
```

### 4. Filter by Category

```bash
curl -X GET "http://localhost:8000/api/v1/products?category=Electronics" \
  -H "Authorization: Bearer <your-token-here>"
```

## Development Tools

- **Pre-commit hooks**: Auto-formatting and linting
  ```bash
  pip install pre-commit
  pre-commit install
  ```

- **Logging**: Logs are written to `logs/app_YYYY-MM-DD.log` and console

## Design Decisions

1. **Layered Architecture**: Separates concerns for maintainability and testability
2. **Async SQLAlchemy**: Enables concurrent request handling
3. **JWT Authentication**: Stateless, scalable authentication
4. **Decimal for Prices**: Prevents floating-point precision issues
5. **Address Snapshots**: Preserves historical order data
6. **Dual Database Support**: SQLite for dev speed, PostgreSQL for production

## License

This project is part of a coding assignment.
