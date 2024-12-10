from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from app.routers.users import get_current_user
from app.schemas import UserCreate, UserResponse, UserLogin
from app.models import User
from app.utils.hashing import Hasher
from app.utils.token import create_access_token, create_refresh_token, verify_refresh_token
from app.config import SessionLocal

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility to create tokens for a user
def create_user_tokens(user: User):
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user and generates tokens.
    """
    try:
        # Check for existing username or email
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the user's password
        hashed_password = Hasher.get_password_hash(user.password)

        # Create a new user object
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            is_online=False,
            last_seen=datetime.utcnow(),
        )

        # Save the user in the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Return the response in the expected format
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            profile_picture=None,
            is_online=new_user.is_online,
            last_seen=new_user.last_seen,
            created_at=new_user.created_at,
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Logs in an existing user and generates new tokens.
    """
    # Fetch the user by username
    db_user = db.query(User).filter(User.email == user.email).first()

    # Verify the user and password
    if not db_user or not Hasher.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Update user login details
    db_user.is_active = True
    db_user.is_online = True
    db_user.last_seen = datetime.utcnow()
    db_user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(db_user)

    # Generate tokens and return the response
    tokens = create_user_tokens(db_user)
    return {**tokens, "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Optionally, update user status when logging out
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_online = False  # Mark the user as offline
    db_user.is_active = False  # Deactivate the user (optional)

    db.commit()
    
    return {"message": "User logged out successfully"}


@router.post("/refresh-token")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refreshes an access token using a valid refresh token.
    """
    try:
        # Verify and decode the refresh token
        payload = verify_refresh_token(refresh_token)
        username = payload.get("sub")

        # Fetch the user by username
        db_user = db.query(User).filter(User.username == username).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a new access token
        access_token = create_access_token({"sub": db_user.username})
        return {"access_token": access_token}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
