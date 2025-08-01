from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Table
from sqlalchemy.orm import relationship
from src.utils.database import Base

# Association table for post tags
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_name', String)
)

class User(Base):
    """SQLAlchemy model for users table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationships
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    reading_list = relationship("ReadingListItem", back_populates="user")

class BlogPost(Base):
    """SQLAlchemy model for blog posts table."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(String)
    category = Column(String, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = Column(Boolean, default=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")
    tags = relationship("Tag", secondary=post_tags, backref="posts")

class Comment(Base):
    """SQLAlchemy model for comments table."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    post = relationship("BlogPost", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Like(Base):
    """SQLAlchemy model for post likes table."""
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship("BlogPost", back_populates="likes")

class Tag(Base):
    """SQLAlchemy model for tags table."""
    __tablename__ = "tags"

    name = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReadingListItem(Base):
    """SQLAlchemy model for reading list items table."""
    __tablename__ = "reading_list"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reading_list")
