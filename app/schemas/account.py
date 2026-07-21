import uuid
from decimal import Decimal

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    balance: Decimal

    model_config = {"from_attributes": True}
