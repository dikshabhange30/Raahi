
from fastapi import FastAPI
from app.database import create_tables

from app.routers.auth import router as auth_router

from app.routers.users import router as users_router  # Connect the users router
 
app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)

create_tables()

@app.get("/")
def root():
    return {"message": "Raahi backend is running"}

