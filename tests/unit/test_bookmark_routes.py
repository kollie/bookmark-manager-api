import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User
from models.bookmark import Bookmark
from auth.auth import get_password_hash

def create_user_and_get_token(client: TestClient, test_user: dict, db_session: Session):
    """    
    Args:
        client (TestClient): The FastAPI test client instance.
        test_user (dict): A dictionary containing test user data.
        db_session (Session): Database session object.
    
    Returns:
        tuple: A tuple containing the created User object and the JWT access token (str).
    """
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/users/login", 
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = login_response.json()["access_token"]
    return user, token

def test_create_bookmark(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Test creating a new bookmark.
    """
    user, token = create_user_and_get_token(client, test_user, db_session)

    response = client.post(
        "/api/v1/bookmarks",
        json=test_bookmark,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "Bookmark creation failed, unexpected status code"
    data = response.json()
    assert data["title"] == test_bookmark["title"], "Bookmark title does not match"
    # Normalize URLs by stripping trailing slashes
    assert data["url"].rstrip("/") == test_bookmark["url"].rstrip("/"), "Bookmark URL does not match"
    assert data["description"] == test_bookmark["description"], "Bookmark description does not match"
    assert data["user_id"] == user.id, "Bookmark user_id does not match the creator's id"

def test_get_bookmarks(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Test retrieving all bookmarks for a specific user.
    """
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    bookmark = Bookmark(**test_bookmark, user_id=user.id)
    db_session.add(bookmark)
    db_session.commit()

    login_response = client.post(
        "/api/v1/users/login", 
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/bookmarks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "Failed to retrieve bookmarks"
    data = response.json()
    assert len(data) == 1, "Unexpected number of bookmarks returned"
    assert data[0]["title"] == test_bookmark["title"], "Returned bookmark title does not match"

def test_get_bookmark(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Test retrieving a specific bookmark by its ID.
    """
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    bookmark = Bookmark(**test_bookmark, user_id=user.id)
    db_session.add(bookmark)
    db_session.commit()

    login_response = client.post(
        "/api/v1/users/login", 
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = login_response.json()["access_token"]

    response = client.get(
        f"/api/v1/bookmarks/{bookmark.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "Failed to retrieve specific bookmark"
    data = response.json()
    assert data["title"] == test_bookmark["title"], "Bookmark title does not match expected"
    assert data["id"] == bookmark.id, "Bookmark ID mismatch"

def test_update_bookmark(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Test updating an existing bookmark.
    """
    user, token = create_user_and_get_token(client, test_user, db_session)

    bookmark = Bookmark(**test_bookmark, user_id=user.id)
    db_session.add(bookmark)
    db_session.commit()

    update_data = {"title": "Updated Title"}
    response = client.put(
        f"/api/v1/bookmarks/{bookmark.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "Bookmark update failed"
    data = response.json()
    assert data["title"] == update_data["title"], "Bookmark title was not updated correctly"
    assert data["id"] == bookmark.id, "Bookmark ID mismatch after update"

def test_delete_bookmark(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Test deleting a bookmark.
    """
    user, token = create_user_and_get_token(client, test_user, db_session)

    bookmark = Bookmark(**test_bookmark, user_id=user.id)
    db_session.add(bookmark)
    db_session.commit()

    response = client.delete(
        f"/api/v1/bookmarks/{bookmark.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204, "Bookmark deletion failed"

    # Remove all instances from the session identity map.
    db_session.expunge_all()
    deleted_bookmark = db_session.query(Bookmark).filter(Bookmark.id == bookmark.id).first()
    assert deleted_bookmark is None, "Deleted bookmark is still accessible"
