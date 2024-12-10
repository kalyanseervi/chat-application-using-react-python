import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, chat, users
from app.models import Base
from app.config import engine
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chat Application API",
    description="API for user authentication and real-time chat functionality.",
    version="1.0.0",
)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Default Vite frontend
    "http://localhost:8000",  # API Server
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {e}")
        raise RuntimeError("Database initialization failed.")

# Log shutdown events
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down.")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Root endpoint
@app.get("/", tags=["General"])
def root():
    """
    Root endpoint to verify API is working.
    """
    return {"message": "Welcome to the Chat Application!"}
