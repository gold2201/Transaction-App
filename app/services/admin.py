import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.account import Account
from app.models.user import User
from app.repositories.account import AccountRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.account_repo = AccountRepository(db)

    async def list_users(self) -> Sequence[User]:
        return await self.user_repo.list_all()

    async def create_user(self, data: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")
        return await self.user_repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
        )

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        update_data = {}
        if data.email is not None:
            update_data["email"] = data.email
        if data.full_name is not None:
            update_data["full_name"] = data.full_name
        if data.password is not None:
            update_data["hashed_password"] = get_password_hash(data.password)
        if update_data:
            user = await self.user_repo.update(
                user,
                email=data.email,
                full_name=data.full_name,
                hashed_password=get_password_hash(data.password) if data.password else None,
            )
        return user

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        await self.user_repo.delete(user)

    async def get_user_accounts(self, user_id: uuid.UUID) -> Sequence[Account]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        return await self.account_repo.get_by_user_id(user_id)
