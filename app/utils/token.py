import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
import logging

# Secret and algorithm configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # For development only
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30  # Refresh token valid for 30 days

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_access_token(data: dict) -> str:
    """
    Create a short-lived access token.
    """
    if not isinstance(data, dict):
        logger.error("Invalid data format for token creation. Expected a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid data format. Expected a dictionary.")

    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Unexpected error during token creation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the access token.")


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived refresh token.
    """
    if not isinstance(data, dict):
        logger.error("Invalid data format for refresh token creation. Expected a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid data format. Expected a dictionary.")

    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Unexpected error during refresh token creation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the refresh token.")


def decode_token(token: str) -> dict:
    """
    Decode and validate a token (access or refresh).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Token error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    except Exception as e:
        logger.error(f"Unexpected error during token decoding: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while decoding the token.")


def validate_token(token: str, required_claims: list = None) -> dict:
    """
    Validate a token and ensure required claims are present.
    """
    try:
        payload = decode_token(token)

        # Validate required claims (e.g., 'sub')
        if required_claims:
            for claim in required_claims:
                if claim not in payload:
                    logger.warning(f"Missing required claim: {claim}")
                    raise HTTPException(status_code=401, detail=f"Missing required claim: {claim}")

        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while validating the token.")


def verify_refresh_token(token: str) -> dict:
    """
    Decode and validate a refresh token specifically.
    """
    try:
        payload = decode_token(token)
        # Optional: Add additional checks for refresh tokens here
        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during refresh token verification: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while verifying the refresh token.")
