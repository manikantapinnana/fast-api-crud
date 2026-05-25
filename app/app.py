from fastapi import Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
from app.core.security.authhandler import get_current_user
from app.routers.auth import auth_router
from app.routers.user import user_router
from app.routers.chat import chat_router
from app.utils.init_db import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup tasks here (e.g., connect to the database)
    print("Starting up...")
    create_tables()
    yield
    # Perform shutdown tasks here (e.g., disconnect from the database)
    print("Shutting down...")

app = FastAPI(lifespan=lifespan, title="User Management API", description="API for user registration, authentication, and management", version="1.0.0")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])
app.include_router(chat_router, prefix="/chats", tags=["chats"], dependencies=[Depends(get_current_user)])


@app.get("/health", tags=["health"], summary="Health Check", description="Check if the API is running and healthy")
def read_root():
    return {"message": "I am alive and healthy!😄"}
