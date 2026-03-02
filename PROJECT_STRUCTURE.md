# Project Structure (Beginner Guide)

This project uses a **flat layout**: all app code lives in the project root. Each file has one clear job.

```
AuthLab/
├── main.py           # FastAPI app + all routes (signup, login, protected)
├── auth.py           # Password hashing + JWT create/verify
├── config.py         # Settings (SECRET_KEY, token expiry, etc.)
├── database.py       # In-memory user store (replace with real DB later)
├── models.py         # Request/response shapes (Pydantic models)
├── requirements.txt  # Python dependencies
├── .env.example      # Example env vars (copy to .env and fill in)
├── README.md         # Full docs + how to run
├── CONCEPTS.md       # Auth flow + key files summary
└── PROJECT_STRUCTURE.md  # This file
```

## Where to Look First

| If you want to…              | Open this file   |
|-----------------------------|------------------|
| See all API endpoints       | `main.py`        |
| Understand signup/login flow| `main.py` → signup, login, get_current_user |
| See how passwords are hashed| `auth.py`        |
| See how JWTs are made/checked | `auth.py`     |
| Change secret or token time | `config.py` or `.env` |
| See what data we accept/send| `models.py`      |
| See how users are stored    | `database.py`    |

## Recommended Reading Order

1. **README.md** – Why auth, types, and how to run the project.
2. **CONCEPTS.md** – Flow: signup → login → protected route.
3. **models.py** – What the API expects and returns.
4. **main.py** – Routes and the `get_current_user` dependency.
5. **auth.py** – Hashing and JWT functions.
6. **config.py** and **database.py** – Settings and storage.

No frameworks or extra layers: just FastAPI, a few modules, and clear names so you can follow the flow end-to-end.
