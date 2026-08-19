
from fastapi import FastAPI
from app.database import create_tables

from app.routers.auth import router as auth_router

from app.routers.users import router as users_router  # Connect the users router

from app.routers.communities import router as communities_router

from app.routers.help_requests import router as help_requests_router

from app.routers.messages import router as messages_router

from app.routers.group_messages import router as group_messages_router

from app.routers.notifications import router as notifications_router
 
app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(communities_router)

app.include_router(help_requests_router)
app.include_router(messages_router)
app.include_router(group_messages_router)

app.include_router(notifications_router)

create_tables()

@app.get("/")
def root():
    return {"message": "Raahi backend is running"}

