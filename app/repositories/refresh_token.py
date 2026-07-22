import uuid
from datetime import datetime

from sqlalchemy import select

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository):
    async def create(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> RefreshToken:
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.db.add(db_token)
        await self.db.flush()
        return db_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        return result.scalar_one_or_none()

    async def revoke(self, token: str) -> None:
        db_token = await self.get_by_token(token)
        if db_token:
            db_token.revoked = True
            await self.db.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,  # noqa: E712
            )
        )
        for t in result.scalars().all():
            t.revoked = True
        await self.db.flush()
