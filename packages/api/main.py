"""FastAPI entry point for the Quick‑Stack experimental backend.

- Provides JWT‑based auth (simple token for demo).
- Uses SQLModel (SQLite for quick local testing; can be switched to Postgres via DATABASE_URL).
- Registers routers for customers and jobs (CRUD stubs).
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, SQLModel, create_engine, select
from datetime import datetime, timedelta
import jwt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quickstack.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

engine = create_engine(DATABASE_URL, echo=False)

# ---------------------------------------------------------------------------
# Models (imported lazily to avoid circular imports)
# ---------------------------------------------------------------------------
from . import models

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Quick‑Stack API", version="0.1.0")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# ---------------------------------------------------------------------------
# Auth utilities
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    with Session(engine) as session:
        user = session.get(models.User, user_id)
        if user is None:
            raise credentials_exception
        return user

# ---------------------------------------------------------------------------
# Token endpoint (demo – password is plain text for simplicity)
# ---------------------------------------------------------------------------
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app you would hash/verify the password.
    with Session(engine) as session:
        statement = select(models.User).where(models.User.email == form_data.username)
        user = session.exec(statement).first()
        if not user or form_data.password != "password":
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

# ---------------------------------------------------------------------------
# Include routers (CRUD for customers & jobs)
# ---------------------------------------------------------------------------
from .routers import customers, jobs

app.include_router(customers.router, prefix="/customers", tags=["customers"], dependencies=[Depends(get_current_user)])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"], dependencies=[Depends(get_current_user)])

# ---------------------------------------------------------------------------
# Student learning site (BA Automation Lab)
# Mounted LAST so every API route above (and /docs) keeps priority.
# ---------------------------------------------------------------------------
from pathlib import Path
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="site")
