from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str
    is_active: bool
    auth_token: str


class TokenData(BaseModel):
    email: EmailStr
    password: str | None = None


class TokenBase(BaseModel):
    access_token: str
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True


class UserToken(User):
    access_token: TokenBase = {}
