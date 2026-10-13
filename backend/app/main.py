
from fastapi import FastAPI

app = FastAPI(
    title="Raahi API",
    description="A community platform that connects newcomers with helpful people.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Raahi!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
