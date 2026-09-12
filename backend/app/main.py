from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.database import Base, engine
from backend.app.models.document import Document
from backend.app.api.document import router as documents_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Document Intelligence API",
    description="AI-powered financial document extraction and validation platform",
    version="1.0.0"
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Include Document API
# --------------------------------------------------

app.include_router(documents_router)


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Document Intelligence API is running"
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy"
    }