from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token, UserUpdate
from auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

router = APIRouter()

@router.post("/users/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint creates a new user with the provided email, username, and password,
    ensuring that both the email and username are unique.

    Args:
        user (UserCreate): The registration data including email, username, and password.
        db (Session): Database session dependency.

    Returns:
        UserResponse: The registered user's data.
    
    Raises:
        HTTPException: If the email or username is already in use.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

