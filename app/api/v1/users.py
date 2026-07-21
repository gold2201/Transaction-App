from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers import users_router
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.payment import Payment
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.payment import PaymentResponse
from app.schemas.user import UserResponse


@users_router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@users_router.get("/me/accounts", response_model=list[AccountResponse])
async def read_current_user_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Sequence[Account]:
    result = await db.execute(select(Account).where(Account.user_id == current_user.id))
    return result.scalars().all()


@users_router.get("/me/payments", response_model=list[PaymentResponse])
async def read_current_user_payments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Sequence[Payment]:
    result = await db.execute(select(Payment).where(Payment.user_id == current_user.id))
    return result.scalars().all()
