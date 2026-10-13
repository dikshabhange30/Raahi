
from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router


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


@app.get("/")
def home():
    return {
        "message": "Welcome to Raahi!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
