from datetime import datetime
from pydantic import BaseModel


class WebsocketMessage(BaseModel):
    content: str


class MessageCreate(BaseModel):
    request_id: int
    receiver_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    request_id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageBroadcast(BaseModel):
    request_id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

