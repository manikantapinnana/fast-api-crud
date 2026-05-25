from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from app.db.repository.chat_requests import ChatRequests
from app.db.repository.userRepo import UserRepository
from app.db.schemas.chat_requests import ChatRequestResponse

class ChatService:
    def __init__(self, sesssion: Session):
        self.__chatRepositary = ChatRequests(sesssion)

    def send_chat_request(self, sender_id: int, receiver_id: int) -> ChatRequestResponse:
        if sender_id == receiver_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send chat request to yourself.")
        user_repo = UserRepository(self.__chatRepositary.session)
        if not user_repo.get_user_by_id(user_id=receiver_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver user not found.")
        if self.__chatRepositary.chat_request_exists(sender_id=sender_id, receiver_id=receiver_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat request already exists.")
        return self.__chatRepositary.create_chat_request(receiver_id, sender_id)
    
    def get_pending_chat_requests_for_user(self, user_id: int):
        return self.__chatRepositary.get_pending_chat_requests_for_user(user_id)
    
    def update_chat_request_status(self, request_id: int, new_status: str):
        if new_status not in ["pending", "accepted", "rejected"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value.")
        if self.__chatRepositary.chat_request_accepted_or_rejected(request_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat request has already been accepted or rejected.")
        updated_request = self.__chatRepositary.update_chat_request_status(request_id, new_status)
        if not updated_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat request not found.")
        return updated_request