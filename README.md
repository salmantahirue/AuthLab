# Authentication Concepts for Python Developers

A learning project for interns: **Why we need authentication**, **types & methods**, and a **working JWT example** in FastAPI.

**New here?** Start with [How to run](#10-how-to-run-this-project), then read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) to see which file does what and in what order to read the code. For request flow, see [API request life cycle](#6-api-request-life-cycle-when-a-request-comes-from-the-frontend) and the step-by-step sections for [signup](#7-step-by-step-signup-api-post-signup), [login](#8-step-by-step-login-api-post-login), and [protected route](#9-step-by-step-protected-api-get-usersme--jwt-required).

---

## 1. Why Do We Need Authentication?

**Authentication** answers: *"Who are you?"*

Without it:
- Anyone could access any user's data (e.g., your bank balance, your profile).
- We couldn't personalize content or restrict actions (e.g., only admins can delete).
- APIs would be open to abuse (bots, scrapers, unauthorized access).

**Simple analogy:**  
A building without a receptionist would let anyone walk into any room. Authentication is like showing an ID at reception so the system knows *who* you are and *what* you're allowed to do.

**Authorization** (often confused with authentication) answers: *"What are you allowed to do?"*  
- **Authentication** = prove identity (login).  
- **Authorization** = check permissions (e.g., "can this user delete this post?").

---

## 2. Types of Authentication

| Type | Meaning | Example |
|------|---------|--------|
| **Something you know** | Password, PIN | Login with email + password |
| **Something you have** | Token, device, key | JWT, OTP on phone, API key |
| **Something you are** | Biometric | Fingerprint, face ID |
| **Multi-factor (MFA)** | Combine 2+ types | Password + SMS code |

In web/API development we mostly use **something you know** (password) and **something you have** (tokens like JWT).

---

## 3. Common Authentication Methods (APIs / Web)

### 3.1 Session-Based (Cookie + Server-Side Session)

- User logs in → server creates a **session** and stores it (e.g., in DB or Redis).
- Server sends a **session ID** in a **cookie** to the browser.
- On each request, browser sends the cookie → server looks up the session and knows the user.

**Pros:** Server has full control; can invalidate sessions.  
**Cons:** Needs server-side storage; harder to scale; not ideal for mobile/non-browser clients.

**Example:** Traditional Django/Flask login with `session['user_id']`.

---

### 3.2 Token-Based (e.g. JWT – JSON Web Token)

- User logs in → server validates credentials and returns a **token** (JWT).
- Client stores the token (e.g., in memory, localStorage, or a cookie) and sends it on each request (usually in header: `Authorization: Bearer <token>`).
- Server **does not store** the token; it only **verifies** the signature and reads the payload.

**Pros:** Stateless (no DB lookup per request); works well for APIs and mobile; easy to use across services.  
**Cons:** Hard to "revoke" before expiry unless you add a blocklist or short expiry + refresh tokens.

**Example:** This project uses JWT.

---

### 3.3 API Keys

- Client sends a fixed secret key (e.g., in header or query).
- Used for machine-to-machine or "developer" access (e.g., `X-API-Key: abc123`).

**Pros:** Simple.  
**Cons:** No notion of "user"; if leaked, full access until rotated.

---

### 3.4 OAuth 2.0 / OpenID Connect

- User logs in via a **third party** (Google, GitHub, etc.).
- Your app gets an **access token** (and optionally user info) from the provider.
- Used for "Login with Google/GitHub".

**Pros:** No password handling; users trust the provider.  
**Cons:** More setup; depends on external provider.

---

## 4. What This Project Demonstrates (JWT in FastAPI)

This project focuses on **token-based authentication using JWT** with:

- **Signup** – register a new user (password hashed, not stored in plain text).
- **Login** – validate credentials and issue a JWT.
- **Protected routes** – only accessible with a valid JWT.
- **How to send the token** – `Authorization: Bearer <token>`.

Concepts you’ll see:

- Password hashing (e.g. bcrypt).
- Creating and verifying JWTs (e.g. `python-jose`).
- Dependency injection in FastAPI to require a valid token.
- Simple in-memory "database" (replace with real DB in production).

---

## 5. Project Life Cycle (When the Server Starts)

When you run `uvicorn main:app --reload`, this is what happens in simple terms:

1. **Python loads `main.py`**  
   - All `import` lines run, so `config.py`, `database.py`, `models.py`, and `auth.py` are loaded too.  
   - No request has arrived yet; we're just preparing the app.

2. **The `app` object is created**  
   - In `main.py`: `app = FastAPI(...)` creates the FastAPI application.  
   - All route decorators (`@app.get(...)`, `@app.post(...)`) register the URLs with the app.

3. **Uvicorn starts listening**  
   - The server waits for HTTP requests (e.g. from a browser or frontend).  
   - When a request comes in, the **API request life cycle** (below) runs.

So: **project life cycle** = load code → create app → register routes → wait for requests.

---

## 6. API Request Life Cycle (When a Request Comes from the Frontend)

When the **frontend** (or any client) sends an API call, the request goes step by step like this:

| Step | What happens | Where (file + code) |
|------|----------------------|----------------------|
| 1 | Request hits the server (e.g. `POST /login` with JSON body). | Network → Uvicorn |
| 2 | **FastAPI** receives the request and finds which **route** matches the URL and method. | `main.py` – FastAPI matches path and method |
| 3 | FastAPI **validates the request body** using the Pydantic model for that route (e.g. `UserLogin`). If the JSON is invalid or missing required fields, FastAPI returns 422 before your route function runs. | `models.py` – e.g. `UserLogin` (email, password) |
| 4 | If the route has **dependencies** (e.g. `Depends(get_current_user)`), FastAPI runs those **first**. If a dependency raises (e.g. 401), the route function never runs. | `main.py` – e.g. `get_current_user()` for protected routes |
| 5 | Your **route function** runs (e.g. `signup()`, `login()`, `get_me()`). Inside it you might call other files (e.g. `auth.py`, `database.py`). | `main.py` – the function under `@app.post(...)` or `@app.get(...)` |
| 6 | The return value is converted to JSON using the **response_model** (e.g. `UserResponse`, `Token`). FastAPI sends this back as the HTTP response. | `main.py` (return) + `models.py` (response shape) |

So in one sentence: **Request → FastAPI (main.py) → optional dependency → your route function → your code in auth/database/models → response.**

---

## 7. Step-by-Step: Signup API (POST /signup)

From the moment the frontend sends `POST /signup` with `{ "email", "password", "full_name" }` until the response is sent, this is the order in which code runs:

| # | File | Code that runs | What it does |
|---|------|----------------|---------------|
| 1 | `main.py` | FastAPI receives the request and matches `POST /signup`. | Routes the request to the `signup` function. |
| 2 | `models.py` | `UserSignup` (Pydantic) | Validates the JSON body: `email` (valid email), `password` (min 6 chars), `full_name` (min 1 char). If invalid → 422. |
| 3 | `main.py` | `signup(data: UserSignup)` is called with the validated `data`. | Entry into your signup logic. |
| 4 | `main.py` | `hash_password(data.password)` | Calls into `auth.py`. |
| 5 | `auth.py` | `hash_password(password)` | Uses bcrypt to hash the password; returns the hash string. |
| 6 | `main.py` | `create_user(email=..., full_name=..., hashed_password=...)` | Calls into `database.py`. |
| 7 | `database.py` | `create_user(...)` | Checks if email already exists (raises `ValueError` if yes). Creates a new user dict with `uuid`, stores it in `fake_users_db`, returns `{ id, email, full_name }` (no password). |
| 8 | `main.py` | `return UserResponse(**user)` | Builds the response using the `UserResponse` model from `models.py` (id, email, full_name). |
| 9 | (FastAPI) | Response is sent as JSON to the client. | Frontend gets the new user info; no token yet (user must login to get a token). |

**Summary:** Frontend → `main.py` (route) → `models.py` (validate body) → `main.py` → `auth.py` (`hash_password`) → `main.py` → `database.py` (`create_user`) → `main.py` → `models.py` (UserResponse) → response.

---

## 8. Step-by-Step: Login API (POST /login)

From the moment the frontend sends `POST /login` with `{ "email", "password" }` until the JWT is returned:

| # | File | Code that runs | What it does |
|---|------|----------------|---------------|
| 1 | `main.py` | FastAPI matches `POST /login`. | Routes to the `login` function. |
| 2 | `models.py` | `UserLogin` (Pydantic) | Validates body: `email`, `password`. If invalid → 422. |
| 3 | `main.py` | `login(data: UserLogin)` is called. | Entry into your login logic. |
| 4 | `main.py` | `get_user_by_email(data.email)` | Calls into `database.py`. |
| 5 | `database.py` | `get_user_by_email(email)` | Looks up the user in `fake_users_db` by email. Returns the user dict or `None`. |
| 6 | `main.py` | If no user or password wrong: `verify_password(...)` or raise 401. | If user not found, we can raise 401. If found, we must verify the password. |
| 7 | `auth.py` | `verify_password(plain_password, hashed_password)` | Compares the submitted password with the stored hash; returns True/False. |
| 8 | `main.py` | If False → raise 401 "Incorrect email or password". | Stops here; no token is returned. |
| 9 | `main.py` | `create_access_token(data={"sub": user["email"]})` | Calls into `auth.py` to create the JWT. |
| 10 | `auth.py` | `create_access_token(data, ...)` | Builds payload with `sub` = email and `exp` = expiry time, signs it with `SECRET_KEY` from `config.py`, returns the JWT string. |
| 11 | `main.py` | `return Token(access_token=access_token, token_type="bearer")` | Builds response using `Token` model from `models.py`. |
| 12 | (FastAPI) | Response is sent as JSON. | Frontend receives `{ "access_token": "<jwt>", "token_type": "bearer" }`. |

**Summary:** Frontend → `main.py` (route) → `models.py` (UserLogin) → `main.py` → `database.py` (`get_user_by_email`) → `main.py` → `auth.py` (`verify_password`, then `create_access_token`) → `main.py` → `models.py` (Token) → response.

---

## 9. Step-by-Step: Protected API (GET /users/me) – JWT Required

When the frontend sends `GET /users/me` **with** the header `Authorization: Bearer <access_token>` (the JWT from login), this is the order of execution:

| # | File | Code that runs | What it does |
|---|------|----------------|---------------|
| 1 | `main.py` | FastAPI matches `GET /users/me`. | Route has `Depends(get_current_user)`, so the dependency runs **before** the route function. |
| 2 | `main.py` | `get_current_user(credentials = Depends(security))` | FastAPI runs this first. `security` (HTTPBearer) reads the `Authorization` header and passes the token (or None). |
| 3 | `main.py` | If `credentials is None` → raise 401. | No token sent → "Not authenticated". |
| 4 | `main.py` | `payload = decode_access_token(token)` | Calls into `auth.py`. |
| 5 | `auth.py` | `decode_access_token(token)` | Verifies the JWT signature with `SECRET_KEY` (from `config.py`), checks expiry. Returns payload `{"sub": "email", "exp": ...}` or `None`. |
| 6 | `main.py` | If `payload is None` → raise 401 "Invalid or expired token". | Stops here if token is bad. |
| 7 | `main.py` | `email = payload.get("sub")`; if no email → 401. | We use `sub` as the user's email. |
| 8 | `main.py` | `get_user_by_email(email)` | Calls into `database.py` to load the full user. |
| 9 | `database.py` | `get_user_by_email(email)` | Returns the user dict from `fake_users_db`. |
| 10 | `main.py` | If no user → 401 "User not found". Else `return user` from `get_current_user`. | The dependency injects this `user` into the route as `current_user`. |
| 11 | `main.py` | `get_me(current_user: dict = Depends(get_current_user))` runs. | Now the actual route function runs with the validated user. |
| 12 | `main.py` | `return UserResponse(id=..., email=..., full_name=...)` | Builds response from `current_user` (no password). |
| 13 | (FastAPI) | Response is sent as JSON. | Frontend gets the current user's profile. |

**Summary:** Frontend (with Bearer token) → `main.py` → dependency `get_current_user` → `auth.py` (`decode_access_token`) → `main.py` → `database.py` (`get_user_by_email`) → back to `main.py` (return user from dependency) → route `get_me` → `UserResponse` → response.

---

## 10. How to Run This Project

```bash
# 1. Create virtual environment (recommended)
python -m venv venv

# 2. Activate it
# Windows (PowerShell or CMD):
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Copy .env.example to .env and set SECRET_KEY for production

# 5. Run the server
uvicorn main:app --reload
```

On Windows you can also double‑click `run.bat` (after creating the venv and installing deps once) to start the server.

Then open:

- **API docs:** http://127.0.0.1:8000/docs  
- **ReDoc:** http://127.0.0.1:8000/redoc  

Try in order:

1. **POST /signup** – register a user.  
2. **POST /login** – get a JWT.  
3. **GET /users/me** – send the JWT in header `Authorization: Bearer <your_token>` and see your profile.

---

## 11. Quick Glossary

| Term | Meaning |
|------|--------|
| **Authentication** | Proving who you are (e.g. login). |
| **Authorization** | Deciding what you’re allowed to do. |
| **JWT** | A signed token (header.payload.signature) that carries claims (e.g. user id, expiry). |
| **Access token** | Token used to access protected resources (short-lived). |
| **Refresh token** | Token used to get a new access token (longer-lived, optional). |
| **Hashing** | One-way transformation (e.g. bcrypt for passwords). Never store plain passwords. |
| **Bearer token** | Convention: send token in header `Authorization: Bearer <token>`. |

---

## 12. What a Python Developer Should Know

- **Why** we need authentication and the difference between authentication and authorization.
- **Types** of auth: password, token, MFA.
- **Methods**: sessions vs tokens (e.g. JWT) vs API keys vs OAuth.
- **Security basics**: hash passwords, use HTTPS, keep secrets out of code, short-lived tokens.
- **In FastAPI**: dependencies to require a valid JWT and get the current user.

This project is a minimal but complete example you can extend (e.g. add a real database, refresh tokens, or roles).
