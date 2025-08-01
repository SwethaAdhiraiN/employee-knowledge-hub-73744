from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from src.utils.database import engine
from src.models import database_models
from src.api.routes import (
    auth,
    posts,
    comments,
    likes,
    reading_list,
    analytics,
    moderation,
    campaigns
)

# Create database tables
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scribbly API",
    description="Backend API for the Scribbly employee blogging platform",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "API health check"},
        {"name": "auth", "description": "Authentication operations"},
        {"name": "users", "description": "User management operations"},
        {"name": "posts", "description": "Blog post operations"},
        {"name": "comments", "description": "Comment operations"},
        {"name": "likes", "description": "Post like operations"},
        {"name": "reading-list", "description": "Reading list operations"},
        {"name": "tags", "description": "Tag operations"},
        {"name": "analytics", "description": "User and platform analytics"},
        {"name": "moderation", "description": "Content moderation tools"},
        {"name": "campaigns", "description": "Writing campaigns and prompts"}
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Scribbly API is running"}

# Include all route modules
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(reading_list.router)
app.include_router(analytics.router)
app.include_router(moderation.router)
app.include_router(campaigns.router)
