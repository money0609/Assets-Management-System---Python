from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create database engine
# Convert postgresql:// to postgresql+psycopg:// for psycopg3
database_url = settings.database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Optional: Test database connection
if __name__ == "__main__":
    try:
        # Try to create a connection
        with engine.connect() as connection:
            print("✅ Database connection successful!")
            print(f"Database URL: {settings.database_url}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct in .env")
