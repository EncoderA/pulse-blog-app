from fastapi import HTTPException, Cookie
from core.security import decode_jwt
from sqlmodel import Session
from core.database import engine

def get_db():
    with Session(engine) as session:
        yield session

def require_admin(access_token: str = Cookie(default=None)):
    if not access_token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = decode_jwt(access_token)
    except Exception:
        raise HTTPException(401, "Invalid token")
        
    if payload.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return payload
