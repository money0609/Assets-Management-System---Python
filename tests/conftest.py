"""
Shared test fixtures and configuration.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
# Import models to ensure tables are registered with Base.metadata
from app.models.asset import Asset  # noqa: F401
from app.models.user import User  # noqa: F401
from main import app

# Use SQLite file-based database for testing
# This ensures all connections can see the same data
import tempfile
import os

# Create a temporary database file
_test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
_test_db_path = _test_db_file.name
_test_db_file.close()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{_test_db_path}"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()  # Commit any pending changes
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency.
    
    Uses the same db_session to ensure data created in db_session
    is visible to API calls made through the client.
    """
    def override_get_db():
        # Use the same session from db_session fixture
        # Ensure any pending changes are flushed
        db_session.flush()
        yield db_session
        # Don't close the session here - db_session fixture handles that
    
    # Ensure models are imported before creating tables
    from app.models.asset import Asset  # noqa: F401
    from app.models.user import User  # noqa: F401
    
    # Disable rate limiting for tests
    from app.core.limiter import limiter
    original_enabled = getattr(limiter, 'enabled', True)
    try:
        limiter.enabled = False
    except AttributeError:
        # If limiter doesn't have enabled attribute, try to clear storage
        if hasattr(limiter, 'storage'):
            limiter.storage.clear()
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()
    try:
        limiter.enabled = original_enabled
    except AttributeError:
        pass

