from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import ChatRoom, ChatRoomMember, Message, Reaction
from app.schemas import MessageResponse, ReactionResponse
from app.config import get_db
from app.utils.token import get_current_user
import json

router = APIRouter()

# Store active WebSocket connections
connected_clients: Dict[int, List[WebSocket]] = {}

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    WebSocket endpoint to handle real-time updates for a chat room.
    """
    # Validate room membership
    is_member = db.query(ChatRoomMember).filter_by(room_id=room_id, user_id=current_user.id).first()
    if not is_member:
        await websocket.close()
        return

    # Add WebSocket connection
    if room_id not in connected_clients:
        connected_clients[room_id] = []
    connected_clients[room_id].append(websocket)

    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "new_message":
                # Save the message in the database
                new_message = Message(
                    content=message["content"],
                    room_id=room_id,
                    sender_id=current_user.id,
                    timestamp=datetime.utcnow(),
                )
                db.add(new_message)
                db.commit()

                # Broadcast the message
                response = MessageResponse(
                    id=new_message.id,
                    sender=current_user,
                    content=new_message.content,
                    timestamp=new_message.timestamp,
                ).dict()
                await broadcast(room_id, {"type": "new_message", "data": response})

            elif message.get("type") == "reaction":
                # Add the reaction to the database
                new_reaction = Reaction(
                    message_id=message["message_id"],
                    user_id=current_user.id,
                    reaction_type=message["reaction"],
                )
                db.add(new_reaction)
                db.commit()

                # Broadcast the reaction
                response = ReactionResponse(
                    id=new_reaction.id,
                    user=current_user,
                    reaction_type=new_reaction.reaction_type,
                ).dict()
                await broadcast(room_id, {"type": "reaction", "data": response})

    except WebSocketDisconnect:
        connected_clients[room_id].remove(websocket)
        if not connected_clients[room_id]:
            del connected_clients[room_id]

async def broadcast(room_id: int, message: dict):
    """
    Broadcast a message to all connected clients in a room.
    """
    for websocket in connected_clients.get(room_id, []):
        await websocket.send_json(message)
