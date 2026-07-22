from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from app.api.routers import users_router
from app.core.deps import get_current_user, get_user_service
from app.models.account import Account
from app.models.payment import Payment
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.payment import PaymentResponse
from app.schemas.user import UserResponse
from app.services.user import UserService


@users_router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@users_router.get("/me/accounts", response_model=list[AccountResponse])
async def read_current_user_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> Sequence[Account]:
    return await user_service.get_accounts(current_user)


@users_router.get("/me/payments", response_model=list[PaymentResponse])
async def read_current_user_payments(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> Sequence[Payment]:
    return await user_service.get_payments(current_user)
