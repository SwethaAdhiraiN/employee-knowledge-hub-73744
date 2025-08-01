from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.models import Comment, CommentCreate, User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import Comment as CommentDB, BlogPost as BlogPostDB

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/{post_id}", response_model=Comment)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a blog post.
    """
    # Check if post exists
    post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create new comment
    db_comment = CommentDB(
        content=comment.content,
        post_id=post_id,
        author_id=current_user.id
    )
    
    db.add(db_comment)
    # Update comment count
    post.comments_count += 1
    db.commit()
    db.refresh(db_comment)
    
    return Comment.from_orm(db_comment)

@router.get("/post/{post_id}", response_model=List[Comment])
async def get_post_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all comments for a specific blog post.
    """
    comments = db.query(CommentDB)\
        .filter(CommentDB.post_id == post_id)\
        .order_by(desc(CommentDB.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return [Comment.from_orm(comment) for comment in comments]

@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int,
    comment_update: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a comment.
    """
    db_comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if db_comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )
    
    db_comment.content = comment_update.content
    db.commit()
    db.refresh(db_comment)
    
    return Comment.from_orm(db_comment)

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment.
    """
    db_comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if db_comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    # Update post comment count
    post = db.query(BlogPostDB).filter(BlogPostDB.id == db_comment.post_id).first()
    if post:
        post.comments_count -= 1
    
    db.delete(db_comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}
