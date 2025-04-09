from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime

class BookmarkBase(BaseModel):
    """
    Base schema that defines the common fields for bookmark operations.
    
    Attributes:
        title (str): The title of the bookmark.
        url (HttpUrl): The URL of the bookmark, validated as a proper HTTP URL.
        description (Optional[str]): An optional description for the bookmark.
    """
    title: str
    url: HttpUrl
    description: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    """
    Schema for creating a new bookmark.
    Inherits all fields from BookmarkBase.
    """
    pass

class BookmarkUpdate(BaseModel):
    """
    Schema for updating an existing bookmark.
    All fields are optional to allow partial updates.
    
    Attributes:
        title (Optional[str]): Updated title for the bookmark.
        url (Optional[HttpUrl]): Updated URL for the bookmark.
        description (Optional[str]): Updated description for the bookmark.
    """
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None

class BookmarkInDB(BookmarkBase):
    model_config = ConfigDict(from_attributes=True)
    """
    Schema representing a bookmark stored in the database.
    
    Attributes:
        id (int): Unique identifier for the bookmark.
        user_id (int): Identifier for the user who owns the bookmark.
        created_at (datetime): Timestamp indicating when the bookmark was created.
        updated_at (Optional[datetime]): Timestamp for the last update, if any.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class BookmarkResponse(BookmarkInDB):
    """
    Schema for returning bookmark data in API responses.
    Inherits all fields from BookmarkInDB.
    """
    pass
