from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from src.models.models import User, BlogPost
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import (
    BlogPost as BlogPostDB,
    Comment as CommentDB,
    User as UserDB
)

router = APIRouter(prefix="/moderation", tags=["moderation"])

@router.get("/posts/reported", response_model=List[BlogPost])
async def get_reported_posts(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of reported posts for moderation. Requires admin access.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # In a real implementation, we would have a reports table
    # For now, we'll just return recent posts for demo
    posts = db.query(BlogPostDB)\
        .order_by(desc(BlogPostDB.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [BlogPost.from_orm(post) for post in posts]

@router.post("/posts/{post_id}/visibility")
async def update_post_visibility(
    post_id: int,
    is_visible: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update post visibility (publish/unpublish). Requires admin access.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post.is_published = is_visible
    db.commit()
    
    return {"message": f"Post {'published' if is_visible else 'unpublished'} successfully"}

@router.post("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user account status (activate/deactivate). Requires admin access.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating own account
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify own account status"
        )
    
    user.is_active = is_active
    db.commit()
    
    return {"message": f"User account {'activated' if is_active else 'deactivated'} successfully"}

@router.get("/search")
async def search_content(
    query: str,
    content_type: Optional[str] = None,  # "posts" or "comments"
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search through content for moderation. Requires admin access.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if content_type == "posts" or content_type is None:
        posts = db.query(BlogPostDB).filter(
            or_(
                BlogPostDB.title.ilike(f"%{query}%"),
                BlogPostDB.content.ilike(f"%{query}%")
            )
        ).order_by(
            desc(BlogPostDB.created_at)
        ).offset(skip).limit(limit).all()
    else:
        posts = []
    
    if content_type == "comments" or content_type is None:
        comments = db.query(CommentDB).filter(
            CommentDB.content.ilike(f"%{query}%")
        ).order_by(
            desc(CommentDB.created_at)
        ).offset(skip).limit(limit).all()
    else:
        comments = []
    
    return {
        "posts": [BlogPost.from_orm(post) for post in posts],
        "comments": comments  # We would need a Comment response model
    }
