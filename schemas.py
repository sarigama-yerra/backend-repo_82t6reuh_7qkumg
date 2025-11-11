"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each class name maps to a collection with its lowercase name.

Examples:
- User -> "user"
- Competition -> "competition"
- LostItem -> "lostitem"
- Event -> "event"
- ForumPost -> "forumpost"
- Comment -> "comment"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="Password hash (sha256)")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    is_active: bool = Field(True, description="Whether user is active")

class Competition(BaseModel):
    title: str = Field(...)
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[datetime] = None
    link: Optional[str] = None

class LostItem(BaseModel):
    title: str = Field(...)
    description: Optional[str] = None
    location: Optional[str] = None
    status: str = Field("lost", description="lost or found")
    contact: Optional[str] = None

class Event(BaseModel):
    title: str = Field(...)
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    link: Optional[str] = None

class ForumPost(BaseModel):
    title: str = Field(...)
    content: str = Field(...)
    author: Optional[str] = None
    tags: Optional[List[str]] = None

class Comment(BaseModel):
    post_id: str = Field(..., description="Related ForumPost ID as string")
    content: str = Field(...)
    author: Optional[str] = None
