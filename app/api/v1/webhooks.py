from typing import Annotated

from fastapi import Depends, HTTPException

from app.api.routers import webhooks_router
from app.core.deps import get_webhook_service
from app.schemas.webhook import WebhookRequest
from app.services.webhook import WebhookService


@webhooks_router.post("/payment")
async def payment_webhook(
    webhook: WebhookRequest,
    webhook_service: Annotated[WebhookService, Depends(get_webhook_service)],
) -> dict[str, str]:
    try:
        return await webhook_service.process_payment(webhook)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
