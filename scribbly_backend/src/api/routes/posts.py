from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.models import BlogPost, BlogPostCreate, BlogPostUpdate, User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import BlogPost as BlogPostDB, User as UserDB, Tag

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=BlogPost)
async def create_post(
    post: BlogPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new blog post.
    """
    user = db.query(UserDB).filter(UserDB.email == current_user.email).first()
    
    # Create new post
    db_post = BlogPostDB(
        title=post.title,
        content=post.content,
        summary=post.summary,
        category=post.category,
        author_id=user.id
    )
    
    # Add tags
    for tag_name in post.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        db_post.tags.append(tag)
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return BlogPost.from_orm(db_post)

@router.get("/", response_model=List[BlogPost])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of blog posts with optional filtering.
    """
    query = db.query(BlogPostDB)
    
    if category:
        query = query.filter(BlogPostDB.category == category)
    
    if tag:
        query = query.filter(BlogPostDB.tags.any(name=tag))
    
    posts = query.order_by(desc(BlogPostDB.created_at)).offset(skip).limit(limit).all()
    return [BlogPost.from_orm(post) for post in posts]

@router.get("/{post_id}", response_model=BlogPost)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    Get a specific blog post by ID.
    """
    post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return BlogPost.from_orm(post)

@router.put("/{post_id}", response_model=BlogPost)
async def update_post(
    post_id: int,
    post_update: BlogPostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a blog post.
    """
    user = db.query(UserDB).filter(UserDB.email == current_user.email).first()
    db_post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if db_post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # Update post fields
    for field, value in post_update.dict(exclude_unset=True).items():
        if field == "tags":
            db_post.tags.clear()
            for tag_name in value:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                db_post.tags.append(tag)
        else:
            setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    
    return BlogPost.from_orm(db_post)

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a blog post.
    """
    user = db.query(UserDB).filter(UserDB.email == current_user.email).first()
    db_post = db.query(BlogPostDB).filter(BlogPostDB.id == post_id).first()
    
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if db_post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    db.delete(db_post)
    db.commit()
    
    return {"message": "Post deleted successfully"}
