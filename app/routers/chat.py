from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
from app.models import User, ChatRoom, ChatRoomMember, Message, Reaction, ReactionType, RoomType, PushSubscription
from app.config import SessionLocal
from app.utils.encryption import encrypt_message, decrypt_message
from app.utils.token import decode_token
import firebase_admin
from firebase_admin import messaging, credentials

import logging
import json
# Initialize Firebase Admin SDK 
cred = credentials.Certificate("F:/Oasis_Infobyte/chat_app/app/firebase_credentials.json")
firebase_admin.initialize_app(cred)

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()
# In-memory store for WebSocket connections by room ID
connected_clients: Dict[int, List[Dict[str, WebSocket]]] = {}
print('i am at chat page')
# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility to extract token from Authorization header
def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print("i am here",credentials.credentials)
    return credentials.credentials

# Utility to fetch the current authenticated user
def get_current_user(db: Session = Depends(get_db), token: str = Depends(get_token_from_header)) -> User:
    print('i am at get')
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Utility function to broadcast messages to all clients in a room
async def broadcast_message(room_id: int, message: dict, exclude_user_id: int = None):
    """Broadcast a message to all WebSocket clients in a room."""
    for client in connected_clients.get(room_id, []):
        if client["user_id"] != exclude_user_id:
            try:
                await client["websocket"].send_json(message)
            except WebSocketDisconnect:
                remove_client_from_room(room_id, client["user_id"])

# Utility function to add a WebSocket client to a room
def add_client_to_room(room_id: int, user_id: int, websocket: WebSocket):
    if room_id not in connected_clients:
        connected_clients[room_id] = []
    connected_clients[room_id].append({"user_id": user_id, "websocket": websocket})
    logger.info(f"User {user_id} connected to room {room_id}.")

# Utility function to remove a WebSocket client from a room
def remove_client_from_room(room_id: int, user_id: int):
    connected_clients[room_id] = [
        c for c in connected_clients.get(room_id, []) if c["user_id"] != user_id
    ]
    if not connected_clients[room_id]:
        del connected_clients[room_id]
    logger.info(f"User {user_id} disconnected from room {room_id}.")

@router.post("/chat-room/private/{friend_id}")
def create_or_get_private_chat_room(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create or retrieve a private chat room between the current user and a friend.
    """
    print('i am at get private chat room')
    # Ensure the friend exists
    friend = db.query(User).filter(User.id == friend_id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")

    # Check if a private chat room already exists
    existing_room = db.query(ChatRoom).filter(
        ChatRoom.type == RoomType.private,
        ChatRoom.members.any(user_id=current_user.id),
        ChatRoom.members.any(user_id=friend_id),
    ).first()
    print('existing room', existing_room)
    if existing_room:
        return {"room_id": existing_room.id}

    # Create a new private chat room
    new_room = ChatRoom(
        name=f"Private Chat {current_user.id}-{friend_id}",
        type=RoomType.private,
        owner_id=current_user.id,
    )
    db.add(new_room)
    db.commit()

    # Add members to the room
    db.add_all([
        ChatRoomMember(room_id=new_room.id, user_id=current_user.id),
        ChatRoomMember(room_id=new_room.id, user_id=friend_id),
    ])
    db.commit()

    return {"room_id": new_room.id}


# Fetch paginated messages from a chat room
@router.get("/chat-room/{room_id}/messages")
def get_chat_room_messages(
    room_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch messages from a chat room with pagination.
    """
    print('i am at old messages')
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    print('thats room ids ',room)
    if not room or not db.query(ChatRoomMember).filter(ChatRoomMember.room_id == room_id, ChatRoomMember.user_id == current_user.id).first():
        raise HTTPException(status_code=403, detail="Not authorized to view this room")

    messages = (
        db.query(Message)
        .filter(Message.room_id == room_id)
        .order_by(Message.timestamp.desc())  # Latest messages first
        .offset(offset)
        .limit(limit)
        .all()
    )

    print('my messages',messages)

    return [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "content": decrypt_message(msg.content),
            "media_url": msg.media_url,
            "timestamp": msg.timestamp,
        }
        for msg in messages
    ]

# FCM Notification Function
def send_fcm_notification(token: str, title: str, body: str):
    print('token in fcm not ',token)
    print('title in fcm ',title)
    print('body in fcm ',body)
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        response = messaging.send(message)
        logger.info(f"Notification sent successfully: {response}")
    except Exception as e:
        logger.error(f"Failed to send FCM notification: {e}")

@router.post("/notifications/subscribe")
def subscribe_to_notifications(
    subscription: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save the FCM token for the current user.
    """
    fcm_token = subscription.get("fcm_token")
    print('fcm token ',fcm_token)

    if not fcm_token:
        raise HTTPException(status_code=400, detail="Invalid subscription data")

    # Check if the token already exists
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == fcm_token).first()
    if existing:
        return {"message": "Subscription already exists"}

    # Save the new subscription
    new_subscription = PushSubscription(
        user_id=current_user.id,
        endpoint=fcm_token,
        p256dh="",  # Not needed for FCM, but retained for compatibility
        auth="",    # Not needed for FCM, but retained for compatibility
    )
    db.add(new_subscription)
    db.commit()
    return {"message": "Subscription added"}


@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: int,
    db: Session = Depends(get_db),
):
    print("I am at socket")
    """
    WebSocket endpoint for chat room communication.
    """
    token = websocket.query_params.get("token")
    print('igot token ', token)
    if not token:
        await websocket.close(code=1008, reason="Token required")
        return

    try:
        current_user = get_current_user(db=db, token=token)
    except HTTPException as e:
        await websocket.close(code=1008, reason=e.detail)
        return

    # Ensure the user is a member of the room
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room or not db.query(ChatRoomMember).filter(ChatRoomMember.room_id == room_id, ChatRoomMember.user_id == current_user.id).first():
        await websocket.close(code=1003, reason="Unauthorized or room does not exist")
        return

    # Accept WebSocket connection
    await websocket.accept()
    add_client_to_room(room_id, current_user.id, websocket)

    # Notify other members
    await broadcast_message(room_id, {"type": "user_joined", "user_id": current_user.id})

    try:
        while True:
            message_data = await websocket.receive_json()

            if message_data.get("type") == "message":
                content = message_data.get("content")
                media_url = message_data.get("media_url", None)
                media_type = message_data.get("media_type", None)

                # Encrypt and save the message
                encrypted_content = encrypt_message(content)
                new_message = Message(
                    room_id=room.id,
                    sender_id=current_user.id,
                    content=encrypted_content,
                    media_url=media_url,
                    media_type=media_type,
                    timestamp=datetime.utcnow(),
                )
                db.add(new_message)
                db.commit()

                # Send push notifications to all room members
                room_members = db.query(ChatRoomMember).filter(
                    ChatRoomMember.room_id == room_id,
                    ChatRoomMember.user_id != current_user.id,
                ).all()
                print('room_members ',room_members)
                for member in room_members:
                    subscriptions = db.query(PushSubscription).filter(
                        PushSubscription.user_id == member.user_id
                    ).all()

                    for sub in subscriptions:
                        send_fcm_notification(sub.endpoint, "New Message", f"{current_user.username}: {content}")
                

                await broadcast_message(room_id, {
                    "type": "new_message",
                    "sender_id": current_user.id,
                    "content": content,
                    "media_url": media_url,
                }, exclude_user_id=current_user.id)

            elif message_data.get("type") == "reaction":
                message_id = message_data.get("message_id")
                reaction = message_data.get("reaction")

                if reaction not in ReactionType._member_names_:
                    await websocket.send_json({"error": "Invalid reaction type"})
                    continue

                message = db.query(Message).filter(Message.id == message_id).first()
                if not message:
                    await websocket.send_json({"error": "Message not found"})
                    continue

                # Add reaction
                new_reaction = Reaction(
                    message_id=message_id,
                    user_id=current_user.id,
                    reaction_type=reaction
                )
                db.add(new_reaction)
                db.commit()

                # Broadcast the reaction
                await broadcast_message(room_id, {
                    "type": "reaction",
                    "message_id": message_id,
                    "user_id": current_user.id,
                    "reaction": reaction,
                })

    except WebSocketDisconnect:
        remove_client_from_room(room_id, current_user.id)
        await broadcast_message(room_id, {"type": "user_left", "user_id": current_user.id})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await websocket.close(code=1011, reason="Server error")
