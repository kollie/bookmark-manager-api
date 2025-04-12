from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token, UserUpdate, UserLogin
from auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

router = APIRouter()

# OAuth2PasswordRequestForm
# It is used to get the username and password from the request
@router.post("/users/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Authenticate a user using form data and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Contains the username and password,
            automatically parsed from form data.
        db (Session): Database session dependency.

    Returns:
        Token: An access token and its type upon successful authentication.
    
    Raises:
        HTTPException: If the credentials are invalid.
    """
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the current authenticated user's data.

    Args:
        current_user (User): The currently authenticated user, obtained via JWT validation.

    Returns:
        UserResponse: The user's profile information.
    """
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the profile of the current authenticated user.

    Args:
        user_update (UserUpdate): The data containing fields to be updated.
        current_user (User): The authenticated user whose profile is being updated.
        db (Session): Database session dependency.

    Returns:
        UserResponse: The updated user profile.
    """
    if user_update.email:
        current_user.email = user_update.email
    if user_update.username:
        current_user.username = user_update.username
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current authenticated user's account.

    Args:
        current_user (User): The authenticated user to be deleted.
        db (Session): Database session dependency.

    Returns:
        None: Successful deletion returns no content.
    """
    db.delete(current_user)
    db.commit()
    return None
