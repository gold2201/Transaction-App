import uuid
from decimal import Decimal

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.payment import Payment
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def create_user(
    db: AsyncSession,
    email: str = "test@example.com",
    full_name: str = "Test User",
    password: str = "test123",
    is_admin: bool = False,
) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        is_admin=is_admin,
    )
    db.add(user)
    await db.flush()
    return user


async def create_account(
    db: AsyncSession,
    user_id: uuid.UUID,
    balance: Decimal = Decimal("0.00"),
) -> Account:
    account = Account(
        id=uuid.uuid4(),
        user_id=user_id,
        balance=balance,
    )
    db.add(account)
    await db.flush()
    return account


async def create_payment(
    db: AsyncSession,
    transaction_id: uuid.UUID,
    user_id: uuid.UUID,
    account_id: uuid.UUID,
    amount: float,
) -> Payment:
    payment = Payment(
        id=uuid.uuid4(),
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
    )
    db.add(payment)
    await db.flush()
    return payment
