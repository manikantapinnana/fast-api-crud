from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from app.db.repository.chat_requests import ChatRequests
from app.db.repository.messages import MessagesRepository
from app.db.repository.userRepo import UserRepository
from app.db.schemas.chat_requests import ChatRequestResponse


class ChatService:
    def __init__(self, sesssion: Session):
        self.__chatRepository = ChatRequests(sesssion)
        self.__messageRepository = MessagesRepository(sesssion)
        self.__userRepository = UserRepository(sesssion)

    def send_chat_request(self, sender_id: int, receiver_id: int) -> ChatRequestResponse:
        if sender_id == receiver_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send chat request to yourself.")
        if not self.__userRepository.get_user_by_id(user_id=receiver_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver user not found.")
        if self.__chatRepository.chat_request_exists(sender_id=sender_id, receiver_id=receiver_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat request already exists.")
        return self.__chatRepository.create_chat_request(receiver_id, sender_id)

    def get_pending_chat_requests_for_user(self, user_id: int):
        return self.__chatRepository.get_pending_chat_requests_for_user(user_id)

    def update_chat_request_status(self, request_id: int, new_status: str, user_id: int):
        request = self.__chatRepository.get_chat_request_by_receiver_id_and_request_id(
            receiver_id=user_id,
            request_id=request_id,
        )
        if not request:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this chat request.")
        if new_status not in ["pending", "accepted", "rejected"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value.")
        if self.__chatRepository.chat_request_accepted_or_rejected(request_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat request has already been accepted or rejected.")
        updated_request = self.__chatRepository.update_chat_request_status(request_id, new_status)
        if not updated_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat request not found.")
        return updated_request

    def get_chat_request_by_id(self, request_id: int):
        return self.__chatRepository.get_chat_request_by_id(request_id)

    def user_belongs_to_request(self, request_id: int, user_id: int):
        request = self.__chatRepository.get_chat_request_for_user(request_id=request_id, user_id=user_id)
        return bool(request)

    def save_chat_message(self, request_id: int, sender_id: int, content: str):
        request = self.__chatRepository.get_chat_request_by_id(request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat request not found.")
        if request.status != "accepted":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat request is not accepted.")
        if sender_id not in [request.sender_id, request.receiver_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this chat request.")

        receiver_id = request.receiver_id if sender_id == request.sender_id else request.sender_id
        return self.__messageRepository.create_message(
            request_id=request_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )

    def get_message_history(self, request_id: int, user_id: int):
        request = self.__chatRepository.get_chat_request_by_id(request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat request not found.")
        if request.status != "accepted":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat request is not accepted.")
        if user_id not in [request.sender_id, request.receiver_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this chat request.")
        return self.__messageRepository.get_messages_by_request(request_id)
