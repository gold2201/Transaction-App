import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.account import AccountRepository
from app.repositories.payment import PaymentRepository
from app.repositories.user import UserRepository
from app.schemas.webhook import WebhookRequest


class WebhookService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.account_repo = AccountRepository(db)
        self.payment_repo = PaymentRepository(db)

    async def process_payment(self, data: WebhookRequest) -> dict[str, str]:
        if not self._verify_signature(data):
            raise ValueError("Invalid signature")

        user = await self.user_repo.get_by_id(data.user_id)
        if not user:
            raise LookupError("User not found")

        account = await self.account_repo.get_by_id_and_user(data.account_id, data.user_id)
        if not account:
            account = await self.account_repo.create(
                user_id=data.user_id,
                account_id=data.account_id,
            )

        existing = await self.payment_repo.get_by_transaction_id(data.transaction_id)
        if existing:
            raise ValueError("Transaction already processed")

        payment = await self.payment_repo.create(
            transaction_id=data.transaction_id,
            user_id=data.user_id,
            account_id=account.id,
            amount=data.amount,
        )

        account.balance += data.amount
        await self.account_repo.db.flush()

        return {
            "status": "success",
            "transaction_id": str(payment.transaction_id),
            "account_id": str(account.id),
            "new_balance": str(account.balance),
        }

    @staticmethod
    def _verify_signature(data: WebhookRequest) -> bool:
        payload = f"{data.account_id}{data.amount}{data.transaction_id}{data.user_id}{settings.SECRET_KEY}"
        computed = hashlib.sha256(payload.encode()).hexdigest()
        return computed == data.signature
