from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for display and login")
    full_name: str = Field(..., description="User's full name")

class UserCreate(UserBase):
    """Model for user creation with password."""
    password: str = Field(..., description="User's password", min_length=8)

class UserUpdate(BaseModel):
    """Model for updating user information."""
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, description="Updated full name")
    bio: Optional[str] = Field(None, description="User biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")

class User(UserBase):
    """Complete user model with system fields."""
    id: int = Field(..., description="Unique user identifier")
    bio: Optional[str] = Field(None, description="User biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")
    created_at: datetime = Field(..., description="User account creation timestamp")
    is_active: bool = Field(True, description="Whether the user account is active")
    is_admin: bool = Field(False, description="Whether the user has admin privileges")

    class Config:
        from_attributes = True

class BlogPostBase(BaseModel):
    """Base blog post model with common fields."""
    title: str = Field(..., description="Blog post title", max_length=200)
    content: str = Field(..., description="Blog post content in rich text format")
    summary: str = Field(..., description="Brief summary of the blog post", max_length=500)
    tags: List[str] = Field(default=[], description="List of tags associated with the post")
    category: str = Field(..., description="Category of the blog post")

class BlogPostCreate(BlogPostBase):
    """Model for creating a new blog post."""
    pass

class BlogPostUpdate(BaseModel):
    """Model for updating a blog post."""
    title: Optional[str] = Field(None, description="Updated blog post title", max_length=200)
    content: Optional[str] = Field(None, description="Updated blog post content")
    summary: Optional[str] = Field(None, description="Updated blog post summary", max_length=500)
    tags: Optional[List[str]] = Field(None, description="Updated list of tags")
    category: Optional[str] = Field(None, description="Updated category")
    is_published: Optional[bool] = Field(None, description="Update publication status")

class BlogPost(BlogPostBase):
    """Complete blog post model with system fields."""
    id: int = Field(..., description="Unique blog post identifier")
    author_id: int = Field(..., description="ID of the post author")
    created_at: datetime = Field(..., description="Post creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_published: bool = Field(True, description="Whether the post is published")
    likes_count: int = Field(0, description="Number of likes on the post")
    comments_count: int = Field(0, description="Number of comments on the post")
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    """Base comment model."""
    content: str = Field(..., description="Comment content")

class CommentCreate(CommentBase):
    """Model for creating a new comment."""
    post_id: int = Field(..., description="ID of the blog post being commented on")

class Comment(CommentBase):
    """Complete comment model with system fields."""
    id: int = Field(..., description="Unique comment identifier")
    post_id: int = Field(..., description="ID of the blog post")
    author_id: int = Field(..., description="ID of the comment author")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

class ReadingListItem(BaseModel):
    """Model for reading list items."""
    id: int = Field(..., description="Unique reading list item identifier")
    user_id: int = Field(..., description="ID of the user")
    post_id: int = Field(..., description="ID of the saved blog post")
    created_at: datetime = Field(..., description="When the item was added to reading list")
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Authentication token model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

class TokenData(BaseModel):
    """Token payload data."""
    email: str = Field(..., description="User email from token")
