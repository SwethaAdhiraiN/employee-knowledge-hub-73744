from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract

from src.models.models import User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import (
    BlogPost as BlogPostDB,
    Like as LikeDB,
    Comment as CommentDB,
    User as UserDB
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/author/{author_id}/stats")
async def get_author_stats(
    author_id: int,
    period: str = "all",  # all, week, month, year
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a specific author.
    """
    # Verify author exists
    author = db.query(UserDB).filter(UserDB.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    # Set time filter based on period
    time_filter = None
    if period != "all":
        now = datetime.utcnow()
        if period == "week":
            time_filter = now - timedelta(days=7)
        elif period == "month":
            time_filter = now - timedelta(days=30)
        elif period == "year":
            time_filter = now - timedelta(days=365)
    
    # Base query for posts
    posts_query = db.query(BlogPostDB).filter(BlogPostDB.author_id == author_id)
    if time_filter:
        posts_query = posts_query.filter(BlogPostDB.created_at >= time_filter)
    
    # Get various stats
    total_posts = posts_query.count()
    total_likes = posts_query.with_entities(func.sum(BlogPostDB.likes_count)).scalar() or 0
    total_comments = posts_query.with_entities(func.sum(BlogPostDB.comments_count)).scalar() or 0
    
    # Get engagement trend (posts per month)
    posts_trend = db.query(
        extract('year', BlogPostDB.created_at).label('year'),
        extract('month', BlogPostDB.created_at).label('month'),
        func.count(BlogPostDB.id).label('count')
    ).filter(
        BlogPostDB.author_id == author_id
    ).group_by(
        extract('year', BlogPostDB.created_at),
        extract('month', BlogPostDB.created_at)
    ).order_by(
        desc('year'),
        desc('month')
    ).limit(12).all()
    
    # Get most popular posts
    popular_posts = posts_query.order_by(
        desc(BlogPostDB.likes_count + BlogPostDB.comments_count)
    ).limit(5).all()
    
    return {
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "posts_trend": [
            {
                "year": int(trend.year),
                "month": int(trend.month),
                "count": trend.count
            } for trend in posts_trend
        ],
        "popular_posts": [
            {
                "id": post.id,
                "title": post.title,
                "likes": post.likes_count,
                "comments": post.comments_count
            } for post in popular_posts
        ]
    }

@router.get("/platform/stats")
async def get_platform_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get platform-wide analytics. Requires admin access.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get various platform stats
    total_users = db.query(UserDB).count()
    total_posts = db.query(BlogPostDB).count()
    total_likes = db.query(LikeDB).count()
    total_comments = db.query(CommentDB).count()
    
    # Active users in last 30 days (users who posted, liked, or commented)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(func.count(func.distinct(UserDB.id))).filter(
        (UserDB.id == BlogPostDB.author_id) & (BlogPostDB.created_at >= thirty_days_ago) |
        (UserDB.id == LikeDB.user_id) & (LikeDB.created_at >= thirty_days_ago) |
        (UserDB.id == CommentDB.author_id) & (CommentDB.created_at >= thirty_days_ago)
    ).scalar()
    
    # Get top categories
    top_categories = db.query(
        BlogPostDB.category,
        func.count(BlogPostDB.id).label('count')
    ).group_by(
        BlogPostDB.category
    ).order_by(
        desc('count')
    ).limit(5).all()
    
    # Get top authors
    top_authors = db.query(
        UserDB.id,
        UserDB.username,
        func.count(BlogPostDB.id).label('post_count'),
        func.sum(BlogPostDB.likes_count).label('total_likes')
    ).join(
        BlogPostDB,
        UserDB.id == BlogPostDB.author_id
    ).group_by(
        UserDB.id,
        UserDB.username
    ).order_by(
        desc('total_likes')
    ).limit(5).all()
    
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "active_users_30d": active_users,
        "top_categories": [
            {
                "category": category,
                "count": count
            } for category, count in top_categories
        ],
        "top_authors": [
            {
                "id": author.id,
                "username": author.username,
                "post_count": author.post_count,
                "total_likes": author.total_likes
            } for author in top_authors
        ]
    }
