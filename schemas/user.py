from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    Base schema for user attributes.

    Attributes:
        email (EmailStr): The user's email address.
        username (str): The unique username for the user.
    """
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """
    Schema used for user creation.

    Inherits from UserBase and adds a password field.

    Attributes:
        password (str): The plain text password for the new user.
    """
    password: str

class UserLogin(BaseModel):
    """
    Schema for user login request.

    Attributes:
        username (str): The user's username.
        password (str): The user's password.
    """
    username: str
    password: str

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.

    All fields are optional to allow partial updates.

    Attributes:
        email (Optional[EmailStr]): New email address if updated.
        username (Optional[str]): New username if updated.
        password (Optional[str]): New plain text password if updated.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    """
    Schema representing a user stored in the database.

    Attributes:
        id (int): The unique identifier for the user.
        created_at (datetime): Timestamp when the user was created.
        updated_at (Optional[datetime]): Timestamp when the user was last updated.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserResponse(UserInDB):
    """
    Schema for user data returned in API responses.
    
    Inherits all fields from UserInDB.
    """
    pass

class Token(BaseModel):
    """
    Schema for JWT token details.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The token type (typically 'Bearer').
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema for data extracted from the JWT token.

    Attributes:
        username (Optional[str]): The username contained in the token.
    """
    username: Optional[str] = None
