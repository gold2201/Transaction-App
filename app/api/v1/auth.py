import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers import auth_router
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.refresh_token import (
    get_refresh_token,
    revoke_refresh_token,
    save_refresh_token,
)
from app.schemas.auth import SignUpRequest, Token, TokenRefresh
from app.schemas.user import UserResponse


@auth_router.post("/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    body: SignUpRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=get_password_hash(body.password),
        is_admin=False,
    )
    db.add(user)
    await db.flush()
    return user


@auth_router.post("/sign-in", response_model=Token)
async def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token_str = create_refresh_token(data={"sub": str(user.id)})
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await save_refresh_token(db, user.id, refresh_token_str, expires_at)

    return Token(access_token=access_token, refresh_token=refresh_token_str)


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    body: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from e

    db_token = await get_refresh_token(db, body.refresh_token)
    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    if db_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    await revoke_refresh_token(db, body.refresh_token)

    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token(data={"sub": str(user.id)})
    new_refresh = create_refresh_token(data={"sub": str(user.id)})
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await save_refresh_token(db, user.id, new_refresh, expires_at)

    return Token(access_token=new_access, refresh_token=new_refresh)


@auth_router.post("/logout")
async def logout(
    body: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    await revoke_refresh_token(db, body.refresh_token)
    return {"detail": "Logged out"}
