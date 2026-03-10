import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import workflows, data

app = FastAPI(
    title="Rekt Automations API",
    description="API to run content and meme generation workflows manually and read automation data.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Welcome to Rekt Automations API! Use /docs for Swagger UI documentation."
    }
