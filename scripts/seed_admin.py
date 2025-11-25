"""
Database seeding script to create the initial admin user.

This script creates the first admin user in the database, which is needed
to register other users through the API.

Usage:
    python scripts/seed_admin.py
    python scripts/seed_admin.py --username admin --password securepass123
"""
import sys
import os
import argparse

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.crud.user import get_user_by_username, get_all_users


def create_admin_user(db: Session, username: str = "admin", password: str = "admin123") -> User:
    """Create an admin user in the database."""
    # Check if username already exists
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise ValueError(f"User '{username}' already exists")
    
    # Hash password
    hashed_password = get_password_hash(password)
    
    # Create admin user
    admin_user = User(
        username=username,
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user


def check_existing_admins(db: Session) -> bool:
    """Check if any admin users exist in the database."""
    users = get_all_users(db)
    return any(user.role == UserRole.ADMIN for user in users)


def main():
    """Main function to seed admin user."""
    parser = argparse.ArgumentParser(description="Create initial admin user in database")
    parser.add_argument(
        "--username",
        type=str,
        default="admin",
        help="Username for admin user (default: admin)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="admin123",
        help="Password for admin user (default: admin123)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force creation even if admin users exist"
    )
    
    args = parser.parse_args()
    
    # Ensure database tables exist
    print("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Check if admin users already exist
        if not args.force and check_existing_admins(db):
            print("⚠️  Admin user(s) already exist in the database.")
            print("   Use --force to create another admin user anyway.")
            return
        
        # Create admin user
        print(f"Creating admin user: {args.username}")
        admin_user = create_admin_user(db, args.username, args.password)
        
        print("✅ Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   ID: {admin_user.id}")
        print(f"\n💡 You can now login with:")
        print(f"   Username: {args.username}")
        print(f"   Password: {args.password}")
        print(f"\n⚠️  IMPORTANT: Change the default password after first login!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

