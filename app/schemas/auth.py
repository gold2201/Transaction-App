import uuid

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6, max_length=100)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: uuid.UUID | None = None


class SignInRequest(BaseModel):
    username: str
    password: str
