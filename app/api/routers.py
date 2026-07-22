from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])
webhooks_router = APIRouter(prefix="/webhooks", tags=["webhooks"])


from app.api.v1 import users, admin, auth, webhooks  # noqa
