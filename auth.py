"""
Authentication utilities: password hashing and JWT create/verify.

LEARNING NOTES FOR BEGINNERS:
- Passwords: We NEVER store plain text. We hash with bcrypt (one-way). Even we can't "reverse" it.
- JWT: A token that contains claims (e.g. user email, expiry). Server signs it with SECRET_KEY.
  The client sends it back on each request; we verify the signature to trust the claims.
- "sub" (subject) in JWT = who the token belongs to (we use email here).
"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from config import settings

# bcrypt has a 72-byte maximum; we truncate so longer passwords don't raise (and match hash/verify)
BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_to_bcrypt_bytes(password: str) -> bytes:
    """Convert password to at most 72 bytes for bcrypt."""
    if isinstance(password, bytes):
        return password[:BCRYPT_MAX_PASSWORD_BYTES]
    return password.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """
    Hash a password before storing. Same password + bcrypt's built-in salt = safe storage.
    Call this only when registering or changing password; never store plain passwords.
    Passwords longer than 72 bytes are truncated to match bcrypt's limit.
    """
    pwd_bytes = _password_to_bcrypt_bytes(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if the password the user entered matches the stored hash.
    Used at login to verify credentials.
    """
    pwd_bytes = _password_to_bcrypt_bytes(plain_password)
    try:
        stored = hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password
    except Exception:
        return False
    return bcrypt.checkpw(pwd_bytes, stored)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT (JSON Web Token) that we send to the client after login.
    - data: usually {"sub": user_email} so we know who the token belongs to.
    - exp: expiry time so the token stops working after a while (see config).
    - Token is signed with SECRET_KEY; only our server can create valid tokens.
    """
    to_encode = data.copy()
    # exp = "expiration" claim; client must send token before this time
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT from the client. Returns the payload (e.g. {"sub": "user@mail.com"}) if valid.
    Returns None if the token is invalid, expired, or tampered with.
    We verify the signature using SECRET_KEY so we know only we issued this token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
