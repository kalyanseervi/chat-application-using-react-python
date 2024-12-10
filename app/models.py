from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    Boolean,
    Enum,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import enum
import magic
from app.config import Base

# Enum for Room Types
class RoomType(enum.Enum):
    private = "private"
    group = "group"

# Enum for Reaction Types
class ReactionType(enum.Enum):
    like = "like"
    love = "love"
    laugh = "laugh"
    angry = "angry"
    sad = "sad"

# Soft deletion mixin
class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)

    @classmethod
    def active(cls, query):
        return query.filter(cls.is_deleted == False)

# Friendship model
class Friendship(Base):
    __tablename__ = "friendships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, declined
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="friendships_as_user")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="friendships_as_friend")

    def __repr__(self):
        return f"<Friendship(id={self.id}, user_id={self.user_id}, friend_id={self.friend_id}, status={self.status})>"

# User model
class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")
    friendships_as_user = relationship("Friendship", foreign_keys=[Friendship.user_id], back_populates="user", cascade="all, delete-orphan")
    friendships_as_friend = relationship("Friendship", foreign_keys=[Friendship.friend_id], back_populates="friend", cascade="all, delete-orphan")
    push_subscriptions = relationship("PushSubscription", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

# ChatRoom model
class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(Enum(RoomType), default=RoomType.group)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages = relationship("Message", order_by="Message.timestamp", back_populates="room")
    members = relationship("ChatRoomMember", back_populates="room", cascade="all, delete-orphan")
    owner = relationship("User", backref="owned_rooms", foreign_keys=[owner_id])

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name={self.name}, type={self.type})>"

# ChatRoomMember model
class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("ChatRoom", back_populates="members")
    user = relationship("User")

    def __repr__(self):
        return f"<ChatRoomMember(room_id={self.room_id}, user_id={self.user_id})>"

# Message model
class Message(Base, SoftDeleteMixin):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    mentions = Column(JSON, nullable=True)  # JSON for mentions
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    reactions = relationship("Reaction", back_populates="message", cascade="all, delete-orphan")
    replies = relationship("Message", backref=backref("parent", remote_side=[id]))

    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender.username}, content={self.content[:20]})>"

    def delete(self):
        self.is_deleted = True
        self.timestamp = datetime.utcnow()

    def validate_media(self):
        if self.media_url and self.media_type:
            allowed_mime_types = {"image/jpeg", "image/png", "video/mp4"}
            mime_type = magic.Magic(mime=True).from_file(self.media_url)
            if mime_type not in allowed_mime_types:
                raise ValueError(f"Unsupported media type: {mime_type}")

    def extract_mentions(self, db_session):
        if self.content:
            mention_usernames = [word[1:] for word in self.content.split() if word.startswith("@")]
            mentioned_users = db_session.query(User).filter(User.username.in_(mention_usernames)).all()
            self.mentions = [user.id for user in mentioned_users]

# Reaction model
class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reaction_type = Column(Enum(ReactionType), nullable=False)

    # Relationships
    message = relationship("Message", back_populates="reactions")
    user = relationship("User", back_populates="reactions")

    def __repr__(self):
        return f"<Reaction(id={self.id}, user_id={self.user_id}, reaction_type={self.reaction_type})>"

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    endpoint = Column(String, nullable=False, unique=True)
    p256dh = Column(String, nullable=False)  # Public key for encryption
    auth = Column(String, nullable=False)    # Auth secret for encryption

    # Unique constraint to ensure each user has unique subscriptions
    __table_args__ = (UniqueConstraint("user_id", "endpoint", name="uq_user_endpoint"),)

    user = relationship("User", back_populates="push_subscriptions")
