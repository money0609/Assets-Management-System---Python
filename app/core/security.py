from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

# Bcrypt has a 72-byte limit for passwords
# All passwords in tests must be <= 72 bytes
BCRYPT_MAX_PASSWORD_BYTES = 72

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Convert password to bytes if it's a string
    password_bytes = plain_password.encode('utf-8')
    # Truncate to 72 bytes if needed
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_BYTES]
    
    # Verify password using bcrypt directly
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))

def get_password_hash(plain_password: str) -> str:
    """
    Hash a password using bcrypt directly.
    
    Note: Bcrypt has a 72-byte limit. Passwords longer than 72 bytes will be truncated.
    All test passwords must be <= 72 bytes to avoid truncation issues.
    """
    # Convert to bytes and truncate to 72 bytes if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_BYTES]
    
    # Hash using bcrypt directly (avoids passlib initialization issues)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None