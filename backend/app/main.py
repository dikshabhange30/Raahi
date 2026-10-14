
from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.communities import router as communities_router
from app.routers.help_requests import router as help_requests_router
from app.routers.conversations import router as conversations_router
from app.routers.community_chat import router as community_chat_router
from app.routers.safety import router as safety_router


app = FastAPI(
    title="Raahi API",
    description="A community platform that connects newcomers with helpful people.",
    version="1.0.0",
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(communities_router)
app.include_router(help_requests_router)
app.include_router(conversations_router)
app.include_router(community_chat_router)
app.include_router(safety_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Raahi!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
