from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models import User, Friendship
from app.config import SessionLocal
from app.schemas import UserResponse
from app.utils.token import decode_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validates the token and retrieves the current logged-in user.
    """
    try:
        payload = decode_token(token)  # Decode the token
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all users except:
    - The current user.
    - Users who are already friends with the current user.
    - Users with a pending friend request from or to the current user.
    """
    # Subquery for users who are friends with the current user
    friend_ids_subquery = db.query(Friendship.friend_id).filter(
        Friendship.user_id == current_user.id,
        Friendship.status == "accepted"
    ).union(
        db.query(Friendship.user_id).filter(
            Friendship.friend_id == current_user.id,
            Friendship.status == "accepted"
        )
    ).subquery()

    # Subquery for users with pending friend requests involving the current user
    pending_request_ids_subquery = db.query(Friendship.friend_id).filter(
        Friendship.user_id == current_user.id,
        Friendship.status == "pending"
    ).union(
        db.query(Friendship.user_id).filter(
            Friendship.friend_id == current_user.id,
            Friendship.status == "pending"
        )
    ).subquery()

    # Exclude current user, friends, and users with pending requests
    users = db.query(User).filter(
        User.id != current_user.id,  # Exclude current user
        User.id.notin_(friend_ids_subquery),  # Exclude friends
        User.id.notin_(pending_request_ids_subquery)  # Exclude users with pending requests
    ).offset(skip).limit(limit).all()

    return users


@router.get("/friends")
def get_friends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query both directions for active friendships but exclude the current user from the result
    friends = db.query(User.id, User.username, User.profile_picture, User.is_online).join(
        Friendship,
        (Friendship.user_id == User.id) | (Friendship.friend_id == User.id)  # Check both directions
    ).filter(
        Friendship.status == "accepted",  # Only fetch accepted friendships
        (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id),  # Current user in either direction
        User.id != current_user.id  # Exclude the current user from the result
    ).all()

    # Return only the relevant fields in the response
    friend_list = [{"userId":friend.id,"username": friend.username, "profile_picture": friend.profile_picture, "is_online": friend.is_online} for friend in friends]
    
    return friend_list





@router.post("/friend-request/{receiver_id}")
def send_friend_request(
    receiver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a friend request to another user.
    """
    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself")

    # Check if the receiver exists
    receiver = db.query(User).filter(User.id == receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if a friend request already exists
    existing_request = db.query(Friendship).filter(
        Friendship.user_id == current_user.id,
        Friendship.friend_id == receiver_id,
    ).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")

    # Create and save the friend request
    friend_request = Friendship(user_id=current_user.id, friend_id=receiver_id, status="pending")
    db.add(friend_request)
    db.commit()
    return {"message": "Friend request sent"}


@router.get("/friend-requests")
def get_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch all pending friend requests for the current user.
    """
    friend_requests = db.query(Friendship).filter(
        Friendship.friend_id == current_user.id, Friendship.status == "pending"
    ).all()
    return [
        {"id": req.id, "user": {"id": req.user.id, "username": req.user.username}}
        for req in friend_requests
    ]


@router.post("/accept-friend-request/{request_id}")
def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accept a pending friend request.
    """
    # Find the friend request
    friend_request = db.query(Friendship).filter(Friendship.id == request_id).first()
    if not friend_request or friend_request.friend_id != current_user.id or friend_request.status != "pending":
        raise HTTPException(status_code=404, detail="Friend request not found or invalid")

    # Update the request status
    friend_request.status = "accepted"
    db.commit()
    return {"message": "Friend request accepted"}
