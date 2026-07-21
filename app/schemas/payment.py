import uuid
from decimal import Decimal

from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    amount: Decimal

    model_config = {"from_attributes": True}
