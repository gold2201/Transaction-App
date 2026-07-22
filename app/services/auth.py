import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import SignUpRequest, Token, TokenRefresh


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def sign_up(self, data: SignUpRequest) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")
        return await self.user_repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
            is_admin=False,
        )

    async def sign_in(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_str = create_refresh_token(data={"sub": str(user.id)})
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.token_repo.create(user.id, refresh_token_str, expires_at)

        return Token(access_token=access_token, refresh_token=refresh_token_str)

    async def refresh(self, body: TokenRefresh) -> Token:
        try:
            payload = decode_token(body.refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid refresh token")
        except Exception as e:
            raise ValueError("Invalid refresh token") from e

        db_token = await self.token_repo.get_by_token(body.refresh_token)
        if not db_token or db_token.revoked:
            raise ValueError("Refresh token revoked or not found")

        if db_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            raise ValueError("Refresh token expired")

        await self.token_repo.revoke(body.refresh_token)

        user_id = uuid.UUID(payload["sub"])
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        new_access = create_access_token(data={"sub": str(user.id)})
        new_refresh = create_refresh_token(data={"sub": str(user.id)})
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.token_repo.create(user.id, new_refresh, expires_at)

        return Token(access_token=new_access, refresh_token=new_refresh)

    async def logout(self, body: TokenRefresh, current_user: User) -> None:
        await self.token_repo.revoke(body.refresh_token)
