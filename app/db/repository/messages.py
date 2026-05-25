from app.db.repository.base import BaseRepository
from app.db.models.messages import Message


class MessagesRepository(BaseRepository):
    def create_message(self, request_id: int, sender_id: int, receiver_id: int, content: str):
        new_message = Message(
            request_id=request_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )
        self.session.add(new_message)
        self.session.commit()
        self.session.refresh(new_message)
        return new_message

    def get_messages_by_request(self, request_id: int):
        return (
            self.session.query(Message)
            .filter(Message.request_id == request_id)
            .order_by(Message.created_at)
            .all()
        )

    def get_messages_for_user_and_request(self, request_id: int, user_id: int):
        return (
            self.session.query(Message)
            .filter(
                Message.request_id == request_id,
                (Message.sender_id == user_id) | (Message.receiver_id == user_id),
            )
            .order_by(Message.created_at)
            .all()
        )