from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
import bcrypt
from sqlmodel import Session, select

from core.config import settings
from core.database import get_db
from core.security import create_jwt
from dependencies import get_current_user
from models.user import User
from schemas.user import UserLogin, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Local auth
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserRead)
def register(body: UserRegister, db: Session = Depends(get_db)):
    existing = db.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=body.name,
        email=body.email,
        password_hash=bcrypt.hashpw(body.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        provider="local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        avatar=user.avatar,
    )


@router.post("/login", response_model=UserRead)
def login(body: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.email == body.email)).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(body.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({"sub": str(user.id), "role": user.role})
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=604800,  # 7 days
    )
    return UserRead(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        avatar=user.avatar,
    )


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return UserRead(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        avatar=user.avatar,
    )


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "Logged out"}


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/oauth/google")
def oauth_google():
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/google"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/callback/google")
async def callback_google(code: str, db: Session = Depends(get_db)):
    # Exchange code for tokens
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/google"
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    token_data = token_resp.json()
    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    # Get user info
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
    userinfo = userinfo_resp.json()

    # Upsert user
    email = userinfo["email"]
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            email=email,
            name=userinfo.get("name", email),
            avatar=userinfo.get("picture"),
            provider="google",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Set JWT cookie and redirect to frontend
    token = create_jwt({"sub": str(user.id), "role": user.role})
    response = RedirectResponse(url=settings.FRONTEND_URL)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=604800,
    )
    return response


# ---------------------------------------------------------------------------
# GitHub OAuth
# ---------------------------------------------------------------------------

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


@router.get("/oauth/github")
def oauth_github():
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": f"{settings.FRONTEND_URL}/auth/callback/github",
        "scope": "read:user user:email",
    }
    url = f"{GITHUB_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/callback/github")
async def callback_github(code: str, db: Session = Depends(get_db)):
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/github"
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Accept": "application/json"},
        )
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    # Get user profile
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            GITHUB_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    github_user = user_resp.json()

    # Get primary email (may not be public)
    email = github_user.get("email")
    if not email:
        async with httpx.AsyncClient() as client:
            emails_resp = await client.get(
                GITHUB_EMAILS_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        emails = emails_resp.json()
        primary = next((e for e in emails if e.get("primary")), None)
        email = primary["email"] if primary else emails[0]["email"]

    # Upsert user
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            email=email,
            name=github_user.get("name") or github_user.get("login", email),
            avatar=github_user.get("avatar_url"),
            provider="github",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Set JWT cookie and redirect to frontend
    token = create_jwt({"sub": str(user.id), "role": user.role})
    response = RedirectResponse(url=settings.FRONTEND_URL)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=604800,
    )
    return response
