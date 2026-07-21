import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


async def save_refresh_token(db: AsyncSession, user_id: uuid.UUID, token: str, expires_at: datetime) -> RefreshToken:
    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(db_token)
    await db.flush()
    return db_token


async def get_refresh_token(db: AsyncSession, token: str) -> RefreshToken | None:
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    db_token = await get_refresh_token(db, token)
    if db_token:
        db_token.revoked = True
        await db.flush()


async def revoke_all_user_tokens(db: AsyncSession, user_id: uuid.UUID) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.revoked = True
    await db.flush()
