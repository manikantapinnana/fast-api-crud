import datetime

from app.db.models.chat_requests import ChatRequest
from app.db.repository.base import BaseRepository


class ChatRequests(BaseRepository):
    def create_chat_request(self, user_id:int, sender_id: int):
        new_request = ChatRequest(sender_id=sender_id, receiver_id=user_id, status="pending")
        self.session.add(new_request)
        self.session.commit()
        self.session.refresh(new_request)
        return new_request
    def chat_request_exists(self, sender_id: int, receiver_id: int):
        request = self.session.query(ChatRequest).filter(
            (ChatRequest.sender_id == sender_id) & (ChatRequest.receiver_id == receiver_id)| (ChatRequest.sender_id == receiver_id) & (ChatRequest.receiver_id == sender_id)
        ).first()
        return bool(request)
    def get_pending_chat_requests_for_user(self, user_id: int):
        requests = self.session.query(ChatRequest).filter(
            ChatRequest.receiver_id == user_id,
            ChatRequest.status == "pending"
        ).all()
        return requests
    def chat_request_accepted_or_rejected(self, request_id: int):
        request = self.session.query(ChatRequest).filter(
            ChatRequest.id == request_id,
            ChatRequest.status.in_(["accepted", "rejected"])
        ).first()
        return bool(request)
    def update_chat_request_status(self, request_id: int, new_status: str):
        request = self.session.query(ChatRequest).filter(ChatRequest.id == request_id).first()
        if request:
            request.status = new_status
            self.session.commit()
            self.session.refresh(request)
            return request
        return None

    def get_chat_request_by_id(self, request_id: int):
        return self.session.query(ChatRequest).filter(ChatRequest.id == request_id).first()

    def get_chat_request_by_receiver_id_and_request_id(self, receiver_id: int, request_id: int):
        return self.session.query(ChatRequest).filter(
            ChatRequest.id == request_id,
            ChatRequest.receiver_id == receiver_id
        ).first()

    def get_chat_request_for_user(self, request_id: int, user_id: int):
        return self.session.query(ChatRequest).filter(
            ChatRequest.id == request_id,
            (ChatRequest.sender_id == user_id) | (ChatRequest.receiver_id == user_id),
        ).first()