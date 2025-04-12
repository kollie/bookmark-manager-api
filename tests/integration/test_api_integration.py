import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.user import User
from models.bookmark import Bookmark
from auth.auth import get_password_hash

def test_full_user_workflow(client: TestClient, test_user: dict, db_session: Session):
    """
    Steps:
      1. Register a new user and verify that the email and username match the input.
      2. Login with the new user's credentials (using form data) and obtain a JWT access token.
      3. Retrieve the user's profile using the access token and verify the email.
      4. Update the user's email and check that the changes are reflected.
      5. Delete the user and confirm deletion by attempting to log in again.
    """
    # Register a new user using JSON (registration endpoint accepts JSON)
    response = client.post("/api/v1/users/register", json=test_user)
    assert response.status_code == 200, "User registration failed"
    user_data = response.json()
    assert user_data["email"] == test_user["email"], "Registered email mismatch"
    assert user_data["username"] == test_user["username"], "Registered username mismatch"

    # Login with the new user using form data
    login_response = client.post(
        "/api/v1/users/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert login_response.status_code == 200, "User login failed"
    token = login_response.json()["access_token"]

    # Get current user profile
    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200, "Could not retrieve user profile"
    me_data = me_response.json()
    assert me_data["email"] == test_user["email"], "Profile email mismatch"

    # Update user email
    update_response = client.put(
        "/api/v1/users/me",
        json={"email": "newemail@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200, "User update failed"
    update_data = update_response.json()
    assert update_data["email"] == "newemail@example.com", "Email update did not persist"

    # Delete user
    delete_response = client.delete(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204, "User deletion failed"

    # Verify deletion by attempting to login again using form data
    login_response = client.post(
        "/api/v1/users/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert login_response.status_code == 401, "Deleted user was still able to log in"


def test_full_bookmark_workflow(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Steps:
      1. Create a test user directly in the database.
      2. Login the user (using form data) and obtain a JWT access token.
      3. Create a bookmark and verify its creation.
      4. Retrieve all bookmarks and then a specific bookmark.
      5. Update the bookmark's title and confirm the update.
      6. Delete the bookmark and verify it can no longer be accessed.
    """
    # Create a user directly in the database
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    # Login to get access token using form data
    login_response = client.post(
        "/api/v1/users/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert login_response.status_code == 200, "User login failed for bookmark workflow"
    token = login_response.json()["access_token"]

    # Create a bookmark
    create_response = client.post(
        "/api/v1/bookmarks",
        json=test_bookmark,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200, "Bookmark creation failed"
    bookmark_data = create_response.json()
    bookmark_id = bookmark_data["id"]

    # Retrieve all bookmarks
    get_all_response = client.get(
        "/api/v1/bookmarks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_all_response.status_code == 200, "Failed to retrieve bookmarks"
    bookmarks = get_all_response.json()
    assert len(bookmarks) == 1, "Unexpected number of bookmarks returned"
    assert bookmarks[0]["id"] == bookmark_id, "Bookmark ID mismatch in list"

    # Retrieve specific bookmark
    get_one_response = client.get(
        f"/api/v1/bookmarks/{bookmark_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_one_response.status_code == 200, "Failed to retrieve the specific bookmark"
    assert get_one_response.json()["id"] == bookmark_id, "Specific bookmark ID mismatch"

    # Update bookmark title
    update_data = {"title": "Updated Title"}
    update_response = client.put(
        f"/api/v1/bookmarks/{bookmark_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200, "Bookmark update failed"
    assert update_response.json()["title"] == update_data["title"], "Bookmark title did not update correctly"

    # Delete the bookmark
    delete_response = client.delete(
        f"/api/v1/bookmarks/{bookmark_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204, "Bookmark deletion failed"

    # Confirm deletion by attempting to retrieve the deleted bookmark
    get_one_response = client.get(
        f"/api/v1/bookmarks/{bookmark_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_one_response.status_code == 404, "Deleted bookmark is still accessible"


def test_bookmark_access_control(client: TestClient, test_user: dict, test_bookmark: dict, db_session: Session):
    """
    Steps:
      1. Create two separate users in the database.
      2. Create a bookmark for the first user.
      3. Login as the second user (using form data) and attempt to access the first user's bookmark.
      4. Verify that access is denied.
    """
    # Create first user
    user1 = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    # Create second user
    user2 = User(
        email="user2@example.com",
        username="user2",
        hashed_password=get_password_hash("password2")
    )
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create a bookmark for user1
    bookmark = Bookmark(**test_bookmark, user_id=user1.id)
    db_session.add(bookmark)
    db_session.commit()

    # Login as user2 using form data
    login_response = client.post(
        "/api/v1/users/login",
        data={
            "username": "user2",
            "password": "password2"
        }
    )
    assert login_response.status_code == 200, "User2 login failed"
    token = login_response.json()["access_token"]

    # Attempt to access user1's bookmark with user2's token
    response = client.get(
        f"/api/v1/bookmarks/{bookmark.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, "User2 should not access User1's bookmark"
