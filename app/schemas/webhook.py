import uuid
from decimal import Decimal

from pydantic import BaseModel


class WebhookRequest(BaseModel):
    transaction_id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    amount: Decimal
    signature: str
