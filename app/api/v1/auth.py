from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.routers import auth_router
from app.core.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import SignUpRequest, Token, TokenRefresh
from app.schemas.user import UserResponse
from app.services.auth import AuthService


@auth_router.post("/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    body: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    try:
        return await auth_service.sign_up(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@auth_router.post("/sign-in", response_model=Token)
async def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    try:
        return await auth_service.sign_in(form_data.username, form_data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    body: TokenRefresh,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    try:
        return await auth_service.refresh(body)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@auth_router.post("/logout")
async def logout(
    body: TokenRefresh,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    await auth_service.logout(body, current_user)
    return {"detail": "Logged out"}
