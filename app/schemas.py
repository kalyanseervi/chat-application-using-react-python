from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enum for Room Types
class RoomType(str, Enum):
    private = "private"
    group = "group"

# Enum for Reaction Types
class ReactionType(str, Enum):
    like = "like"
    love = "love"
    laugh = "laugh"
    angry = "angry"
    sad = "sad"

# User creation schema
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3 and 50 characters.")
    email: EmailStr = Field(..., description="Valid email address.")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters.")


#User login schema
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address.")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters.")
    
# User response schema
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_picture: Optional[str] = None
    is_online: bool
    last_seen: datetime
    created_at: datetime

    class Config:
        orm_mode = True

# Friendship schema
class FriendshipResponse(BaseModel):
    id: int
    user: UserResponse
    friend: UserResponse
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# ChatRoom creation schema
class ChatRoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Room name must be between 1 and 100 characters.")
    type: Optional[RoomType] = RoomType.group

# ChatRoom response schema
class ChatRoomResponse(BaseModel):
    id: int
    name: str
    type: RoomType
    is_private: bool
    owner: UserResponse
    members: List[UserResponse] = []  # List of members
    created_at: datetime

    class Config:
        orm_mode = True

# Message creation schema
class MessageCreate(BaseModel):
    content: str = Field(..., max_length=5000, description="Message content cannot exceed 5000 characters.")
    room_id: int
    media_url: Optional[str] = Field(None, description="Optional URL for media content.")
    media_type: Optional[str] = Field(None, description="Optional media type (e.g., image, video).")

# Message response schema
class MessageResponse(BaseModel):
    id: int
    sender: UserResponse
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    mentions: List[UserResponse] = []  # List of mentioned users
    reactions: List["ReactionResponse"] = []  # List of reactions on the message
    timestamp: datetime

    class Config:
        orm_mode = True

# Reaction response schema
class ReactionResponse(BaseModel):
    id: int
    message_id: int
    user: UserResponse
    reaction_type: ReactionType

    class Config:
        orm_mode = True
