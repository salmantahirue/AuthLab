"""
Pydantic models: the "contract" for API request and response bodies.

BEGINNER TIP: FastAPI uses these to validate incoming JSON and to document
the API in /docs. We never expose hashed_password in any response.
"""
from pydantic import BaseModel, EmailStr, Field


# ----- Request models (what the client sends in the body) -----

class UserSignup(BaseModel):
    """Body for POST /signup. EmailStr ensures valid email format."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    full_name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    """Body for POST /login. On success the response includes access_token (JWT)."""
    email: EmailStr
    password: str


# ----- Response models (what we send back to the client) -----

class Token(BaseModel):
    """Returned by POST /login. Client should send access_token in Authorization header."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User info in API responses. Never includes password or hashed_password."""
    id: str
    email: str
    full_name: str
