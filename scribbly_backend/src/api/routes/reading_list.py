from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.models import BlogPost, User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import ReadingListItem as ReadingListItemDB, BlogPost as BlogPostDB

router = APIRouter(prefix="/reading-list", tags=["reading-list"])

@router.post("/{post_id}")
async def add_to_reading_list(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add or remove a post from the user's reading list.
    """
    # Check if post exists
    post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if post is already in reading list
    existing_item = db.query(ReadingListItemDB).filter(
        ReadingListItemDB.post_id == post_id,
        ReadingListItemDB.user_id == current_user.id
    ).first()
    
    if existing_item:
        # Remove from reading list
        db.delete(existing_item)
        db.commit()
        return {"message": "Post removed from reading list"}
    else:
        # Add to reading list
        new_item = ReadingListItemDB(
            post_id=post_id,
            user_id=current_user.id
        )
        db.add(new_item)
        db.commit()
        return {"message": "Post added to reading list"}

@router.get("/", response_model=List[BlogPost])
async def get_reading_list(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's reading list.
    """
    reading_list = db.query(BlogPostDB)\
        .join(ReadingListItemDB)\
        .filter(ReadingListItemDB.user_id == current_user.id)\
        .order_by(desc(ReadingListItemDB.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [BlogPost.from_orm(post) for post in reading_list]

@router.get("/{post_id}/status")
async def get_reading_list_status(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a post is in the user's reading list.
    """
    item = db.query(ReadingListItemDB).filter(
        ReadingListItemDB.post_id == post_id,
        ReadingListItemDB.user_id == current_user.id
    ).first()
    
    return {"in_reading_list": bool(item)}
