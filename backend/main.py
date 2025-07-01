from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
import uuid
from datetime import datetime, timedelta

app = FastAPI()

# --- CORS ---
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Фейковые данные ---
FAKE_USER = {
    "username": "user", 
    "password": "password",
    "role": "admin",
}

ACTIVE_TOKENS = {}

# --- Модель ответа для токена ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Проверка токена и срока действия ---
def get_current_user(authorization: Annotated[str, Header()]):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    token = authorization.split(" ")[1]

    user_data = ACTIVE_TOKENS.get(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    created_at = user_data["created_at"]
    if datetime.utcnow() - created_at > timedelta(hours=1):
        del ACTIVE_TOKENS[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    return user_data

# --- Логин ---
@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != FAKE_USER["username"] or form_data.password != FAKE_USER["password"]:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    
    token = str(uuid.uuid4())
    ACTIVE_TOKENS[token] = {
        "username": FAKE_USER["username"],
        "role": FAKE_USER["role"],
        "created_at": datetime.utcnow(),
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": FAKE_USER["role"],
    }

# --- Проверка роли ---
def get_current_admin_user(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# --- Эндпоинт для админа ---
@app.get("/api/admin-data")
async def admin_data(admin: dict = Depends(get_current_admin_user)):
    return {"message": f"Добро пожаловать на админ-панель, {admin['username']}"}

# --- Защищённые данные ---
@app.get("/api/secret-data")
async def get_secret_data(user: dict = Depends(get_current_user)):
    return {"message": f"Привет, {user['username']}! Секретное сообщение: 42."}

# --- Выход (logout) ---
@app.post("/api/logout")
async def logout(authorization: Annotated[str, Header()]):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    token = authorization.split(" ")[1]

    if token in ACTIVE_TOKENS:
        del ACTIVE_TOKENS[token]
        return {"detail": "Logged out successfully"}
    raise HTTPException(status_code=401, detail="Invalid token")
