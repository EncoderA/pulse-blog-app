from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel
from core.config import settings
from core.security import create_jwt, decode_jwt

router = APIRouter(tags=["auth"])

class LoginBody(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(body: LoginBody, response: Response):
    if (body.username != settings.ADMIN_USERNAME or
            body.password != settings.ADMIN_PASSWORD):
        raise HTTPException(401, "Invalid credentials")
    token = create_jwt({"sub": settings.ADMIN_USERNAME, "role": "admin"})
    response.set_cookie(
        "access_token", token,
        httponly=True, samesite="lax", max_age=604800
    )
    return {"message": "logged in", "username": settings.ADMIN_USERNAME}

@router.get("/me")
def me(access_token: str = Cookie(default=None)):
    if not access_token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = decode_jwt(access_token)
    except Exception:
        raise HTTPException(401, "Invalid token")
    return {"username": payload["sub"], "role": payload.get("role")}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "logged out"}
