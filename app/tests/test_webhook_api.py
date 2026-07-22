import hashlib
import uuid
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.tests.factories import create_account, create_user


def _make_signature(transaction_id: str, user_id: str, account_id: str, amount: str) -> str:
    payload = f"{account_id}{amount}{transaction_id}{user_id}{settings.SECRET_KEY}"
    return hashlib.sha256(payload.encode()).hexdigest()


class TestWebhookPayment:
    async def test_success_new_account(self, client: AsyncClient, db_session: AsyncSession) -> None:
        user = await create_user(db_session, email="webhook@test.com")
        txn_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())
        amount = "100.00"
        sig = _make_signature(txn_id, str(user.id), account_id, amount)

        response = await client.post(
            "/webhooks/payment",
            json={
                "transaction_id": txn_id,
                "user_id": str(user.id),
                "account_id": account_id,
                "amount": amount,
                "signature": sig,
            },
        )
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["status"] == "success"
        assert data["new_balance"] == "100.00"

    async def test_success_existing_account(self, client: AsyncClient, db_session: AsyncSession) -> None:
        user = await create_user(db_session, email="webhook2@test.com")
        account = await create_account(db_session, user_id=user.id, balance=Decimal("50.00"))
        txn_id = str(uuid.uuid4())
        amount = "25.50"
        sig = _make_signature(txn_id, str(user.id), str(account.id), amount)

        response = await client.post(
            "/webhooks/payment",
            json={
                "transaction_id": txn_id,
                "user_id": str(user.id),
                "account_id": str(account.id),
                "amount": amount,
                "signature": sig,
            },
        )
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["new_balance"] == "75.50"

    async def test_invalid_signature(self, client: AsyncClient, db_session: AsyncSession) -> None:
        user = await create_user(db_session, email="webhook3@test.com")
        txn_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())

        response = await client.post(
            "/webhooks/payment",
            json={
                "transaction_id": txn_id,
                "user_id": str(user.id),
                "account_id": account_id,
                "amount": "100.00",
                "signature": "invalid_signature",
            },
        )
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]

    async def test_duplicate_transaction(self, client: AsyncClient, db_session: AsyncSession) -> None:
        user = await create_user(db_session, email="webhook4@test.com")
        account = await create_account(db_session, user_id=user.id)
        txn_id = str(uuid.uuid4())
        amount = "100.00"
        sig = _make_signature(txn_id, str(user.id), str(account.id), amount)

        await client.post(
            "/webhooks/payment",
            json={
                "transaction_id": txn_id,
                "user_id": str(user.id),
                "account_id": str(account.id),
                "amount": amount,
                "signature": sig,
            },
        )

        response = await client.post(
            "/webhooks/payment",
            json={
                "transaction_id": txn_id,
                "user_id": str(user.id),
                "account_id": str(account.id),
                "amount": amount,
                "signature": sig,
            },
        )
        assert response.status_code == 400
        assert "already processed" in response.json()["detail"].lower()

    async def test_user_not_found(self, client: AsyncClient) -> None:
        txn_id = str(uuid.uuid4())
        fake_user_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())
        sig = _make_signature(txn_id, fake_user_id, account_id, "100.00")

        response = await client.post(
            "/webhooks/payment",
            json={
                "transaction_id": txn_id,
                "user_id": fake_user_id,
                "account_id": account_id,
                "amount": "100.00",
                "signature": sig,
            },
        )
        assert response.status_code == 404
