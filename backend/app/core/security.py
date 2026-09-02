import warnings
import logging
import types

# ── Silence bcrypt/passlib version mismatch at startup ───────────────────────
# bcrypt >= 4.1 removed __about__; passlib tries to read it.
# Inject a dummy __about__ so passlib doesn't throw AttributeError.
try:
    import bcrypt as _bcrypt_mod
    if not hasattr(_bcrypt_mod, "__about__"):
        _about = types.ModuleType("bcrypt.__about__")
        _about.__version__ = getattr(_bcrypt_mod, "__version__", "4.0.1")
        _bcrypt_mod.__about__ = _about
except Exception:
    pass

warnings.filterwarnings("ignore", message=".*error reading bcrypt.*", category=UserWarning)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.CRITICAL)
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_password(password: str) -> str:
    """Bcrypt only hashes up to 72 bytes. Truncate safely to avoid errors."""
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        encoded = encoded[:72]
    return encoded.decode("utf-8", errors="ignore")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed password safely without raising 500s."""
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(_truncate_password(plain_password), hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash a plain password securely. Truncates to bcrypt's 72-byte limit."""
    return pwd_context.hash(_truncate_password(password))

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
