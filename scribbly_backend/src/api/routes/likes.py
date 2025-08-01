from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.models import User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import Like as LikeDB, BlogPost as BlogPostDB

router = APIRouter(prefix="/likes", tags=["likes"])

@router.post("/{post_id}")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like or unlike a blog post.
    """
    # Check if post exists
    post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user already liked the post
    existing_like = db.query(LikeDB).filter(
        LikeDB.post_id == post_id,
        LikeDB.user_id == current_user.id
    ).first()
    
    if existing_like:
        # Unlike the post
        db.delete(existing_like)
        post.likes_count -= 1
        db.commit()
        return {"message": "Post unliked successfully"}
    else:
        # Like the post
        new_like = LikeDB(
            post_id=post_id,
            user_id=current_user.id
        )
        db.add(new_like)
        post.likes_count += 1
        db.commit()
        return {"message": "Post liked successfully"}

@router.get("/{post_id}/status")
async def get_like_status(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the current user has liked a specific post.
    """
    like = db.query(LikeDB).filter(
        LikeDB.post_id == post_id,
        LikeDB.user_id == current_user.id
    ).first()
    
    return {"liked": bool(like)}
