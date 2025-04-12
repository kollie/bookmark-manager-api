from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.bookmark import Bookmark
from schemas.bookmark import BookmarkCreate, BookmarkResponse, BookmarkUpdate
from auth.auth import get_current_user

router = APIRouter()

@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new bookmark for the current user.

    Args:
        bookmark (BookmarkCreate): Data required for creating a bookmark.
        current_user (User): The currently authenticated user.
        db (Session): Database session dependency.

    Returns:
        BookmarkResponse: The created bookmark.
    """

    db_bookmark = bookmark.model_dump()
    db_bookmark["url"] = str(db_bookmark["url"])
    
    db_bookmark = Bookmark(**db_bookmark, user_id=current_user.id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def read_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all bookmarks for the current authenticated user.

    Args:
        current_user (User): The currently authenticated user.
        db (Session): Database session dependency.

    Returns:
        List[BookmarkResponse]: A list of bookmarks.
    """
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    return bookmarks

@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def read_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a single bookmark by its ID for the authenticated user.

    Args:
        bookmark_id (int): The ID of the bookmark to retrieve.
        current_user (User): The currently authenticated user.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the bookmark is not found or does not belong to the user.

    Returns:
        BookmarkResponse: The bookmark that matches the ID.
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    return bookmark

@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    bookmark_update: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing bookmark of the current user.

    Args:
        bookmark_id (int): The ID of the bookmark to update.
        bookmark_update (BookmarkUpdate): The data to update in the bookmark.
        current_user (User): The currently authenticated user.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the bookmark does not exist or does not belong to the user.

    Returns:
        BookmarkResponse: The updated bookmark.
    """
    db_bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if db_bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    update_data = bookmark_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "url":
            value = str(value)
        setattr(db_bookmark, key, value)
    
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a bookmark belonging to the current user.

    Args:
        bookmark_id (int): The ID of the bookmark to delete.
        current_user (User): The currently authenticated user.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the bookmark is not found.

    Returns:
        None
    """
    db_bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if db_bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    db.delete(db_bookmark)
    db.commit()
    return None
