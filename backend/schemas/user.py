from typing import Optional

from pydantic import BaseModel


class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True
