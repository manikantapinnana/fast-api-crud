from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security.authhandler import get_current_user, get_current_user_from_token
from app.db.schemas.chat_requests import ChatRequestResponse, ChatRequestStatus
from app.db.schemas.messages import WebsocketMessage, MessageResponse
from app.service.chatservice import ChatService

chat_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # map request_id -> list of tuples (WebSocket, user_id)
        self.active_connections: dict[int, list[tuple[WebSocket, int]]] = {}

    async def connect(self, request_id: int, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.setdefault(request_id, []).append((websocket, user_id))

    def disconnect(self, request_id: int, websocket: WebSocket):
        connections = self.active_connections.get(request_id)
        if not connections:
            return
        # remove tuple or websocket matching this websocket
        for pair in list(connections):
            if isinstance(pair, tuple):
                ws = pair[0]
            else:
                ws = pair
            if ws is websocket:
                connections.remove(pair)
        if not connections:
            self.active_connections.pop(request_id, None)

    async def broadcast(self, request_id: int, message: dict, receiver_id: int | None = None, sender_id: int | None = None):
        # send only to the intended receiver's connections, and skip sender's own connection(s)
        conns = list(self.active_connections.get(request_id, []))
        print(f"Broadcast to request {request_id}: {len(conns)} connection(s), receiver={receiver_id}, sender={sender_id}")
        for entry in conns:
            if isinstance(entry, tuple):
                websocket, user_id = entry
            else:
                websocket, user_id = entry, None

            if sender_id is not None and user_id == sender_id:
                continue
            if receiver_id is not None and user_id != receiver_id:
                continue

            try:
                await websocket.send_json(message)
            except Exception as exc:
                # log and clean up bad connection
                print(f"WebSocket send error for request {request_id}, user {user_id}:", exc)
                try:
                    self.disconnect(request_id, websocket)
                except Exception:
                    pass

websocket_manager = ConnectionManager()

@chat_router.post("/send_request", response_model=ChatRequestResponse)
async def send_chat_request(receiver_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    sender_id = current_user.id
    return ChatService(db).send_chat_request(sender_id, receiver_id)

@chat_router.get("/requests", response_model=list[ChatRequestResponse])
async def get_pending_chat_requests_for_user(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.id
    return ChatService(db).get_pending_chat_requests_for_user(user_id)

@chat_router.put("/requests/{request_id}/status", response_model=ChatRequestResponse)
async def update_chat_request_status(request_id: int, new_status: ChatRequestStatus, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return ChatService(db).update_chat_request_status(request_id, new_status, current_user.id)

@chat_router.get("/requests/{request_id}/messages", response_model=list[MessageResponse])
async def get_chat_message_history(request_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return ChatService(db).get_message_history(request_id, current_user.id)

@chat_router.websocket("/ws/{request_id}")
async def websocket_chat_endpoint(websocket: WebSocket, request_id: int, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    try:
        current_user = get_current_user_from_token(token, db)
        if not ChatService(db).user_belongs_to_request(request_id, current_user.id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        request = ChatService(db).get_chat_request_by_id(request_id)
        if not request or request.status != "accepted":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket_manager.connect(request_id, websocket, current_user.id)
        while True:
            try:
                payload = await websocket.receive_json()
                ws_message = WebsocketMessage.model_validate(payload)
                persisted_message = ChatService(db).save_chat_message(request_id, current_user.id, ws_message.content)
                broadcast_payload = MessageResponse.model_validate(persisted_message).model_dump(mode="json")
                print("Broadcasting message:", broadcast_payload)
                await websocket_manager.broadcast(
                    request_id,
                    broadcast_payload,
                    receiver_id=persisted_message.receiver_id,
                    sender_id=current_user.id,
                )
            except WebSocketDisconnect:
                websocket_manager.disconnect(request_id, websocket)
                break
            except Exception:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                break
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    