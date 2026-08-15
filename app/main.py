
from fastapi import FastAPI
from app.database import create_tables

app = FastAPI()

create_tables()

@app.get("/")
def root():
    return {"message": "Raahi backend is running"}

