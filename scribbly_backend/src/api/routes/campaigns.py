from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.models.models import User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.models.database_models import (
    BlogPost as BlogPostDB,
    User as UserDB
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# In a real implementation, we would have Campaign and Prompt models
# For now, we'll use hardcoded data for demonstration

SAMPLE_PROMPTS = [
    {
        "id": 1,
        "title": "Share Your Success Story",
        "description": "Write about a recent project success and the lessons learned.",
        "category": "Professional Growth",
        "points": 50
    },
    {
        "id": 2,
        "title": "Innovation Corner",
        "description": "Describe an innovative solution you developed or encountered.",
        "category": "Innovation",
        "points": 75
    }
]

SAMPLE_CAMPAIGNS = [
    {
        "id": 1,
        "title": "Technical Excellence Month",
        "description": "Share your technical knowledge and best practices.",
        "start_date": datetime.utcnow() - timedelta(days=15),
        "end_date": datetime.utcnow() + timedelta(days=15),
        "prompts": [SAMPLE_PROMPTS[0]],
        "status": "active"
    },
    {
        "id": 2,
        "title": "Innovation Challenge",
        "description": "Document and share innovative solutions.",
        "start_date": datetime.utcnow() + timedelta(days=7),
        "end_date": datetime.utcnow() + timedelta(days=37),
        "prompts": [SAMPLE_PROMPTS[1]],
        "status": "upcoming"
    }
]

@router.get("/active")
async def get_active_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get currently active writing campaigns.
    """
    now = datetime.utcnow()
    active_campaigns = [
        campaign for campaign in SAMPLE_CAMPAIGNS
        if campaign["start_date"] <= now <= campaign["end_date"]
    ]
    
    return active_campaigns

@router.get("/prompts")
async def get_writing_prompts(
    campaign_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get writing prompts, optionally filtered by campaign.
    """
    if campaign_id:
        campaign = next(
            (c for c in SAMPLE_CAMPAIGNS if c["id"] == campaign_id),
            None
        )
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        return campaign["prompts"]
    
    return SAMPLE_PROMPTS

@router.get("/leaderboard")
async def get_campaign_leaderboard(
    campaign_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for writing campaigns.
    """
    # In a real implementation, we would track points in a dedicated table
    # For now, we'll use post counts as points
    top_authors = db.query(
        UserDB.id,
        UserDB.username,
        func.count(BlogPostDB.id).label('post_count')
    ).join(
        BlogPostDB,
        UserDB.id == BlogPostDB.author_id
    ).group_by(
        UserDB.id,
        UserDB.username
    ).order_by(
        desc('post_count')
    ).limit(10).all()
    
    return [
        {
            "user_id": author.id,
            "username": author.username,
            "points": author.post_count * 50  # Simulate points
        }
        for author in top_authors
    ]

@router.post("/prompts/{prompt_id}/submit")
async def submit_prompt_response(
    prompt_id: int,
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a blog post as a response to a writing prompt.
    """
    # Verify prompt exists
    prompt = next(
        (p for p in SAMPLE_PROMPTS if p["id"] == prompt_id),
        None
    )
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Verify post exists and belongs to user
    post = db.query(BlogPostDB).filter(
        BlogPostDB.id == post_id,
        BlogPostDB.author_id == current_user.id
    ).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or unauthorized"
        )
    
    # In a real implementation, we would record this in a submissions table
    return {
        "message": "Post submitted successfully",
        "points_earned": prompt["points"]
    }
