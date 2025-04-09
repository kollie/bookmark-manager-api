from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Bookmark(Base):
    """
    Bookmark model representing a bookmark entry in the database.
    
    Attributes:
        id (int): The unique identifier for the bookmark.
        title (str): The title of the bookmark.
        url (str): The URL of the bookmarked resource.
        description (str, optional): A brief description of the bookmark.
        user_id (int): The foreign key linking the bookmark to its owner.
        created_at (datetime): The timestamp when the bookmark was created.
        updated_at (datetime): The timestamp when the bookmark was last updated.
    """
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Establish a relationship to the User model.
    user = relationship("User", back_populates="bookmarks")
