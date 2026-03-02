# Authentication Concepts - Quick Reference for Interns

## Flow in This Project

```
1. SIGNUP (POST /signup)
   Client sends: { "email", "password", "full_name" }
   → We hash the password (bcrypt)
   → We store user in "DB" (in-memory here)
   → We return user info (no token yet)

2. LOGIN (POST /login)
   Client sends: { "email", "password" }
   → We find user, verify password against stored hash
   → We create a JWT with "sub" = email, "exp" = expiry
   → We return { "access_token": "<jwt>", "token_type": "bearer" }

3. PROTECTED ROUTE (e.g. GET /users/me)
   Client sends header: Authorization: Bearer <access_token>
   → FastAPI dependency (get_current_user) runs first
   → It extracts the token, decodes it, checks signature and expiry
   → If valid, it loads the user and injects it into the route
   → Route returns user-specific data
```

## Key Files

See **PROJECT_STRUCTURE.md** for the full tree and a "where to look first" table.

| File | Purpose |
|------|--------|
| `main.py` | Routes: signup, login, /users/me (protected); dependency `get_current_user` |
| `auth.py` | Hash password, create JWT, verify JWT |
| `config.py` | SECRET_KEY, algorithm, token expiry (override via `.env`) |
| `database.py` | Store/fetch users (in-memory for demo) |
| `models.py` | Request/response schemas (signup, login, user) |
| `.env.example` | Example env vars; copy to `.env` and set SECRET_KEY for production |

## Security Takeaways

1. **Never store plain text passwords** – always hash (e.g. bcrypt).
2. **Keep SECRET_KEY secret** – use env vars in production.
3. **Use HTTPS** – so the token is not sent in clear text.
4. **Short-lived access tokens** – 15–30 min typical; use refresh tokens for longer sessions if needed.
5. **Never put secrets in frontend code** – JWT is sent by the client but created by the server.

## Testing with Swagger UI (/docs)

1. **Signup:** POST /signup with body `{"email":"a@b.com","password":"hello12","full_name":"Test User"}`.
2. **Login:** POST /login with same email/password → copy `access_token` from response.
3. **Authorize:** Click "Authorize", enter `Bearer <your_access_token>` (or just the token in some UIs).
4. **Call GET /users/me** – you should see your profile.
