"""
Simple in-memory "database" for demo/learning. Data is lost when the server restarts.

BEGINNER NOTE: In a real app you'd use PostgreSQL, SQLite, or MongoDB with a library
like SQLAlchemy. This file keeps the project easy to run without any DB setup.
We never store plain-text passwords—only the hash returned by auth.hash_password().
"""
from typing import Dict, Optional
import uuid

# Key = email (lowercase), Value = user dict with id, email, full_name, hashed_password
fake_users_db: Dict[str, dict] = {}


def get_user_by_email(email: str) -> Optional[dict]:
    """Find a user by email. Returns None if not found."""
    return fake_users_db.get(email.lower())


def create_user(email: str, full_name: str, hashed_password: str) -> dict:
    """Create and store a new user. Returns the created user (without password)."""
    email_lower = email.lower()
    if fake_users_db.get(email_lower):
        raise ValueError("User with this email already exists")
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": email_lower,
        "full_name": full_name,
        "hashed_password": hashed_password,
    }
    fake_users_db[email_lower] = user
    return {"id": user_id, "email": user["email"], "full_name": user["full_name"]}
