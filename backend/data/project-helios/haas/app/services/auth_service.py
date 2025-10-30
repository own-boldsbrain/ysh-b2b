from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import redis
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.config import settings
from app.database import SessionLocal
from app.database.models import User as UserDB
from app.models.auth import TokenData, User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Redis client for token blacklist
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
except Exception:
    redis_client = None  # Fallback if Redis not available


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token (valid for 7 days)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(
    token: str,
    credentials_exception,
    expected_type: str = "access"
) -> TokenData:
    """Verify and decode JWT token."""
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        if email is None:
            raise credentials_exception

        # Verify token type
        if token_type != expected_type:
            raise credentials_exception

        token_data = TokenData(email=email, token_type=token_type)
        return token_data
    except JWTError:
        raise credentials_exception


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    db: Session = SessionLocal()
    try:
        user_db = db.query(UserDB).filter(UserDB.email == email).first()
        if not user_db:
            return None
        if not verify_password(password, user_db.hashed_password):
            return None

        return User(
            id=user_db.id,
            email=user_db.email,
            full_name=user_db.username,  # Using username as full_name for now
            role=user_db.role,
            is_active=user_db.is_active,
        )
    finally:
        db.close()


def get_user(email: str) -> Optional[User]:
    """Get user by email."""
    db: Session = SessionLocal()
    try:
        user_db = db.query(UserDB).filter(UserDB.email == email).first()
        if not user_db:
            return None

        return User(
            id=user_db.id,
            email=user_db.email,
            full_name=user_db.username,  # Using username as full_name for now
            role=user_db.role,
            is_active=user_db.is_active,
        )
    finally:
        db.close()


def add_token_to_blacklist(token: str, expires_in: int = 3600) -> bool:
    """Add token to blacklist (Redis)."""
    if not redis_client:
        return False
    try:
        redis_client.setex(
            f"blacklist:{token}",
            expires_in,
            "revoked"
        )
        return True
    except Exception:
        return False


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    if not redis_client:
        return False
    try:
        return redis_client.exists(f"blacklist:{token}") > 0
    except Exception:
        return False
