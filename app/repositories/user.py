import uuid

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, email: str, full_name: str, hashed_password: str, is_admin: bool = False) -> User:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_admin=is_admin,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(
        self,
        user: User,
        email: str | None = None,
        full_name: str | None = None,
        hashed_password: str | None = None,
    ) -> User:
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if hashed_password is not None:
            user.hashed_password = hashed_password
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()

    async def list_all(self) -> list[User]:
        result = await self.db.execute(select(User))
        return list(result.scalars().all())
