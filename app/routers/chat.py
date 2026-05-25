from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security.authhandler import get_current_user
from app.db.schemas.chat_requests import ChatRequestResponse, ChatRequestStatus
from app.service.chatservice import ChatService

chat_router = APIRouter()

@chat_router.post("/send_request", response_model= ChatRequestResponse)
async def send_chat_request(receiver_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    print(current_user.id)
    sender_id=current_user.id
    return ChatService(db).send_chat_request(sender_id, receiver_id)

@chat_router.get("/requests", response_model=list[ChatRequestResponse])
async def get_pending_chat_requests_for_user(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.id
    return ChatService(db).get_pending_chat_requests_for_user(user_id)

@chat_router.put("/requests/{request_id}/status", response_model=ChatRequestResponse)
async def update_chat_request_status(request_id: int, new_status: ChatRequestStatus, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return ChatService(db).update_chat_request_status(request_id, new_status)
    