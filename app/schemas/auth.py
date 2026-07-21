import uuid

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: uuid.UUID | None = None


class LoginRequest(BaseModel):
    email: str
    password: str
