# Airport Asset Management API

A RESTful API for managing airport assets built with FastAPI, PostgreSQL, and SQLAlchemy. This API provides secure authentication, role-based access control, and comprehensive asset management capabilities.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👥 **Role-Based Access Control (RBAC)** - Four user roles: Admin, Manager, Staff, Viewer
- 📦 **Asset Management** - Full CRUD operations for airport assets
- 🛡️ **Rate Limiting** - Protection against API abuse
- 📝 **Auto-Generated API Documentation** - Interactive Swagger UI at `/docs`
- 🧪 **Comprehensive Testing** - Unit, integration, and end-to-end tests
- 🔒 **Password Security** - Bcrypt password hashing
- ✅ **Input Validation** - Pydantic schema validation

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd airport_asset_api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/airport_assets
ENVIRONMENT=development
DEBUG=true

# Security Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important:** 
- Replace `DATABASE_URL` with your PostgreSQL connection string
- Generate a secure `SECRET_KEY` (you can use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- In production, set `ENVIRONMENT=production` and `DEBUG=false`

### 5. Database Setup

1. Create a PostgreSQL database:

```sql
CREATE DATABASE airport_assets;
```

2. Update the `DATABASE_URL` in your `.env` file with your database credentials.

3. The database tables will be created automatically when you start the application.

### 6. Create Initial Admin User

Before you can use the API, you need to create an admin user:

```bash
# Using default credentials (admin/admin123)
python scripts/seed_admin.py

# Or with custom credentials
python scripts/seed_admin.py --username myadmin --password SecurePass123
```

**Security Note:** Change the default admin password after first login!

## Running the Application

### Development Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### Production Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

The Swagger UI provides an interactive interface where you can:
- View all available endpoints
- Test endpoints directly
- Authenticate using the "Authorize" button

## Authentication

### Getting an Access Token

1. Use the `/auth/login` endpoint or the "Authorize" button in Swagger UI
2. Enter your username and password
3. You'll receive an access token

### Using the Token

Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

In Swagger UI:
1. Click the "Authorize" button (lock icon)
2. Enter your credentials
3. Click "Authorize"
4. All protected endpoints will automatically use your token

## User Roles and Permissions

| Role    | View Assets | Create Assets | Update Assets | Delete Assets | Manage Users |
|---------|-------------|---------------|---------------|---------------|--------------|
| Viewer  | ✅          | ❌            | ❌            | ❌            | ❌           |
| Staff   | ✅          | ✅            | ❌            | ❌            | ❌           |
| Manager | ✅          | ✅            | ✅            | ❌            | ❌           |
| Admin   | ✅          | ✅            | ✅            | ✅            | ✅           |

## API Endpoints

### Authentication

- `POST /auth/login` - Login and get access token
- `POST /auth/register` - Register new user (Admin only)
- `GET /auth/me` - Get current user information
- `DELETE /auth/users/{user_id}` - Delete user (Admin only)

### Assets

- `GET /assets/` - List all assets (Public)
- `GET /assets/{asset_id}` - Get asset by ID (Authenticated)
- `POST /assets/create` - Create new asset (Staff, Manager, Admin)
- `PUT /assets/update/{asset_id}` - Update asset (Manager, Admin)
- `DELETE /assets/delete/{asset_id}` - Delete asset (Admin only)

## Testing

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run specific test file:

```bash
pytest tests/test_auth.py -v
```

Run specific test:

```bash
pytest tests/test_auth.py::test_login_success -v
```

### Test Coverage

- **Unit Tests** - Individual function testing
- **Integration Tests** - Database and API integration
- **End-to-End Tests** - Full workflow testing
- **Role-Based Tests** - Permission verification

## Project Structure

```
airport_asset_api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── assets.py      # Asset endpoints
│   │       └── auth.py        # Authentication endpoints
│   ├── core/
│   │   ├── auth.py            # Authentication dependencies
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database connection
│   │   ├── limiter.py         # Rate limiting
│   │   └── security.py        # Password hashing & JWT
│   ├── crud/
│   │   ├── asset.py           # Asset CRUD operations
│   │   └── user.py            # User CRUD operations
│   ├── models/
│   │   ├── asset.py           # Asset database model
│   │   └── user.py             # User database model
│   └── schemas/
│       ├── asset.py            # Asset Pydantic schemas
│       └── user.py             # User Pydantic schemas
├── scripts/
│   └── seed_admin.py          # Create initial admin user
├── tests/
│   ├── conftest.py            # Test fixtures
│   ├── test_auth.py           # Authentication tests
│   ├── test_protected_assets.py  # Protected route tests
│   ├── test_roles.py          # Role-based access tests
│   └── ...                     # Other test files
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- `/auth/login`: 5 requests per minute
- `/auth/register`: 3 requests per hour
- `/assets/create`: 20 requests per minute
- `/assets/update/{id}`: 30 requests per minute
- `/assets/delete/{id}`: 10 requests per minute
- `/assets/`: 100 requests per minute

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response.

## Security Features

- **Password Hashing:** Bcrypt with automatic truncation for passwords > 72 bytes
- **JWT Tokens:** Secure token-based authentication
- **Role-Based Access:** Granular permission control
- **Input Validation:** Pydantic schema validation
- **SQL Injection Protection:** SQLAlchemy ORM prevents SQL injection
- **CORS:** Configurable Cross-Origin Resource Sharing

## Development

### Adding New Endpoints

1. Create/update schema in `app/schemas/`
2. Add CRUD functions in `app/crud/`
3. Create route in `app/api/routes/`
4. Include router in `main.py`
5. Write tests in `tests/`

### Database Migrations

Currently using `Base.metadata.create_all()` for table creation. For production, consider using Alembic for migrations.

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env` file
- Ensure database exists
- Verify credentials are correct

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.10+)

### Authentication Issues

- Verify admin user exists: `python scripts/seed_admin.py`
- Check token expiration time
- Ensure `SECRET_KEY` is set in `.env`

## Technologies Used

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **Pydantic** - Data validation
- **JWT** - Token-based authentication
- **Bcrypt** - Password hashing
- **Pytest** - Testing framework
- **SlowAPI** - Rate limiting

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [open an issue](link-to-issues) or contact the development team.

