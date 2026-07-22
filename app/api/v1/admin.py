import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.routers import admin_router
from app.core.deps import get_admin_service, get_current_admin
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.admin import AdminService


@admin_router.get("/users", response_model=list[UserResponse])
async def list_users(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    _: User = Depends(get_current_admin),
) -> Sequence[User]:
    return await admin_service.list_users()


@admin_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    _: User = Depends(get_current_admin),
) -> User:
    try:
        return await admin_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@admin_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    _: User = Depends(get_current_admin),
) -> User:
    try:
        return await admin_service.update_user(user_id, user_data)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    _: User = Depends(get_current_admin),
) -> None:
    try:
        await admin_service.delete_user(user_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@admin_router.get("/users/{user_id}/accounts", response_model=list[AccountResponse])
async def get_user_accounts(
    user_id: uuid.UUID,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    _: User = Depends(get_current_admin),
) -> Sequence[Account]:
    try:
        return await admin_service.get_user_accounts(user_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
