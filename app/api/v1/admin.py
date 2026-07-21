import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers import admin_router
from app.core.deps import get_current_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate


@admin_router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: User = Depends(get_current_admin),
) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()


@admin_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: User = Depends(get_current_admin),
) -> User:
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    await db.flush()
    return user


@admin_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: User = Depends(get_current_admin),
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    await db.flush()
    return user


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: User = Depends(get_current_admin),
) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.flush()
    return None


@admin_router.get("/users/{user_id}/accounts", response_model=list[AccountResponse])
async def get_user_accounts(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: User = Depends(get_current_admin),
) -> Sequence[Account]:
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    return result.scalars().all()
