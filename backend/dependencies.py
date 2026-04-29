from fastapi import Depends, HTTPException, Cookie, Header
from sqlmodel import Session
from core.database import get_db
from core.security import decode_jwt
from core.config import settings
from models.user import User


def get_current_user(
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_jwt(access_token)
    user = db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_agent(x_api_key: str = Header(default=None)):
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid agent API key")
