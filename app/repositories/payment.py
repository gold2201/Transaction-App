import uuid
from decimal import Decimal

from sqlalchemy import select

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository):
    async def get_by_transaction_id(self, transaction_id: uuid.UUID) -> Payment | None:
        result = await self.db.execute(select(Payment).where(Payment.transaction_id == transaction_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Payment]:
        result = await self.db.execute(select(Payment).where(Payment.user_id == user_id))
        return list(result.scalars().all())

    async def create(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
        account_id: uuid.UUID,
        amount: Decimal,
    ) -> Payment:
        payment = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
        )
        self.db.add(payment)
        await self.db.flush()
        return payment
