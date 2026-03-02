"""
FastAPI JWT Authentication Example – Signup, Login, Protected Routes

BEGINNER FLOW:
1. Signup (POST /signup) → register user, hash password, store in "DB"
2. Login (POST /login)   → verify credentials, return JWT
3. Protected (GET /users/me) → client sends header "Authorization: Bearer <token>"; we validate and return user

The key idea: get_current_user is a FastAPI dependency that runs before protected routes
and only allows the request if the JWT is valid. See CONCEPTS.md for the full flow.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth import hash_password, verify_password, create_access_token, decode_access_token
from config import settings
from database import get_user_by_email, create_user, fake_users_db
from models import UserSignup, UserLogin, Token, UserResponse

app = FastAPI(
    title="JWT Auth Example for Interns",
    description="Signup, Login, and protected routes using JWT. See README and PROJECT_STRUCTURE.md.",
    version="1.0.0",
)

# Tells FastAPI we expect the client to send: Authorization: Bearer <token>
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """
    Dependency: extracts JWT from Authorization header and validates it.
    If valid, returns the user dict; otherwise raises 401 Unauthorized.
    This is how we "protect" routes - only callers with a valid token get through.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Send header: Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # We stored "sub" (subject) as user email in the token
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ----- Public routes -----

@app.get("/")
def root():
    """Public: no auth required."""
    return {
        "message": "JWT Auth Example API",
        "docs": "/docs",
        "signup": "POST /signup",
        "login": "POST /login",
        "protected": "GET /users/me (requires Authorization: Bearer <token>)",
    }


@app.post("/signup", response_model=UserResponse)
def signup(data: UserSignup):
    """
    Register a new user.
    - Password is hashed (never stored in plain text).
    - Returns user info; use /login to get a JWT.
    """
    try:
        hashed = hash_password(data.password)
        user = create_user(email=data.email, full_name=data.full_name, hashed_password=hashed)
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/login", response_model=Token)
def login(data: UserLogin):
    """
    Authenticate with email + password. On success, returns a JWT (access_token).
    Use this token in the header: Authorization: Bearer <access_token>
    """
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create JWT with "sub" = email (subject claim - who this token belongs to)
    access_token = create_access_token(data={"sub": user["email"]})
    return Token(access_token=access_token, token_type="bearer")


# ----- Protected routes (require valid JWT) -----

@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile. Requires valid JWT in Authorization header.
    Example: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
    )


@app.get("/users/list")
def list_users(current_user: dict = Depends(get_current_user)):
    """
    Example: only authenticated users can see the user list.
    In real apps you'd add authorization (e.g. admin only) separately.
    """
    return {
        "users": [
            {"id": u["id"], "email": u["email"], "full_name": u["full_name"]}
            for u in fake_users_db.values()
        ]
    }
