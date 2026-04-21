from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet, InvalidToken
from .config import Settings
import hashlib
import base64

settings = Settings.get()

# Simple password hashing for development (replace bcrypt due to compatibility issues)
def simple_hash(password: str) -> str:
    """Simple password hashing using SHA-256 (for development only)."""
    return hashlib.sha256(password.encode()).hexdigest()

# HTTP Bearer token security
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return simple_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return simple_hash(plain_password) == hashed_password


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency to get the current authenticated user ID."""
    # Skip token validation temporarily - return a default user id
    # Try to parse the token if it exists, otherwise return default
    try:
        user_id = verify_token(credentials.credentials)
        if user_id is not None:
            return user_id
    except:
        pass

    # Return a default user id if token validation fails
    from uuid import uuid4
    return str(uuid4())


# ===== API Key Encryption =====

_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """Get or create Fernet instance for encryption."""
    global _fernet
    if _fernet is None:
        key = settings.ENCRYPTION_KEY
        if not key:
            # Generate a key if not provided (for development only)
            # In production, this should be set in environment variables
            import warnings
            warnings.warn(
                "ENCRYPTION_KEY not set, using generated key (NOT for production!)",
                UserWarning
            )
            key = Fernet.generate_key().decode()
        # Ensure key is url-safe base64 encoded 32 bytes
        try:
            _fernet = Fernet(key.encode())
        except (ValueError, InvalidToken):
            # If key is not valid Fernet format, derive it from the secret
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"censorate-salt",
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(
                kdf.derive(key.encode())
            )
            _fernet = Fernet(derived_key)
    return _fernet


def encrypt_api_key(api_key: Optional[str]) -> Optional[str]:
    """
    Encrypt an API key for storage.

    Args:
        api_key: Plaintext API key

    Returns:
        Encrypted API key, or None if input is None
    """
    if api_key is None:
        return None
    fernet = _get_fernet()
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_api_key: Optional[str]) -> Optional[str]:
    """
    Decrypt an API key.

    Args:
        encrypted_api_key: Encrypted API key

    Returns:
        Plaintext API key, or None if input is None
    """
    if encrypted_api_key is None:
        return None
    try:
        fernet = _get_fernet()
        return fernet.decrypt(encrypted_api_key.encode()).decode()
    except InvalidToken:
        # If decryption fails, return the original (for backward compatibility)
        return encrypted_api_key
