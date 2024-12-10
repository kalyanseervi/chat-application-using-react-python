
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = "sqlite:///./test.db"

# Check if DATABASE_URL is set properly
if not DATABASE_URL:
    raise HTTPException(status_code=500, detail="Database URL is not set in environment variables.")

# Create a database engine with connection pooling for better performance
try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, pool_size=10, max_overflow=20)
    print("Database connection established.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to connect to the database: {str(e)}")

# SessionLocal is the session factory to use for creating sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


