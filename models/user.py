from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    User model representing an application user.
    
    Attributes:
        id (int): Unique identifier of the user.
        email (str): Unique email address of the user.
        username (str): Unique username for the user.
        hashed_password (str): Hashed password for secure authentication.
        created_at (datetime): Timestamp indicating when the user was created.
        updated_at (datetime): Timestamp updated on changes to the user record.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to Bookmark, matching the back_populates from Bookmark
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
