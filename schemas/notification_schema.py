from typing import Optional

from pydantic import BaseModel, Field


class WebPushKeys(BaseModel):
    p256dh: str = Field(..., min_length=1)
    auth: str = Field(..., min_length=1)


class WebPushSubscriptionRequest(BaseModel):
    endpoint: str = Field(..., min_length=1)
    expirationTime: Optional[int] = None
    keys: WebPushKeys


class DeleteWebPushSubscriptionRequest(BaseModel):
    endpoint: str = Field(..., min_length=1)
