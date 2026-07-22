from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.payment import Payment
from app.models.user import User
from app.repositories.account import AccountRepository
from app.repositories.payment import PaymentRepository


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.account_repo = AccountRepository(db)
        self.payment_repo = PaymentRepository(db)

    async def get_accounts(self, user: User) -> Sequence[Account]:
        return await self.account_repo.get_by_user_id(user.id)

    async def get_payments(self, user: User) -> Sequence[Payment]:
        return await self.payment_repo.get_by_user_id(user.id)
