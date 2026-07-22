import uuid

from sqlalchemy import select

from app.models.account import Account
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository):
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Account]:
        result = await self.db.execute(select(Account).where(Account.user_id == user_id))
        return list(result.scalars().all())

    async def get_by_id_and_user(self, account_id: uuid.UUID, user_id: uuid.UUID) -> Account | None:
        result = await self.db.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID, account_id: uuid.UUID | None = None) -> Account:
        account = Account(
            id=account_id or uuid.uuid4(),
            user_id=user_id,
            balance=0,
        )
        self.db.add(account)
        await self.db.flush()
        return account
