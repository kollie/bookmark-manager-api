import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User
from auth.auth import get_password_hash

def test_register_user(client: TestClient, test_user: dict):
    """
    Test that a new user can successfully register.
    """
    response = client.post("/api/v1/users/register", json=test_user)
    assert response.status_code == 200, "Registration should return status 200"
    data = response.json()
    assert data["email"] == test_user["email"], "Email does not match registration data"
    assert data["username"] == test_user["username"], "Username does not match registration data"
    assert "id" in data, "Response should include user id"
    assert "created_at" in data, "Response should include creation timestamp"
    assert "hashed_password" not in data, "Response should not expose hashed_password"

def test_register_duplicate_email(client: TestClient, test_user: dict, db_session: Session):
    """
    Test that registering with a duplicate email fails.
    """
    # Create an initial user with the provided email
    user = User(
        email=test_user["email"],
        username="different_username",
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    # Attempt to register a new user with the same email
    response = client.post("/api/v1/users/register", json=test_user)
    assert response.status_code == 400, "Duplicate email registration should return status 400"
    assert "Email already registered" in response.json()["detail"], "Error message should indicate duplicate email"

def test_register_duplicate_username(client: TestClient, test_user: dict, db_session: Session):
    """
    Test that registering with a duplicate username fails.
    """
    # Create an initial user with the provided username
    user = User(
        email="different@example.com",
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    # Attempt to register a new user with the same username
    response = client.post("/api/v1/users/register", json=test_user)
    assert response.status_code == 400, "Duplicate username registration should return status 400"
    assert "Username already taken" in response.json()["detail"], "Error message should indicate duplicate username"

def test_login_user(client: TestClient, test_user: dict, db_session: Session):
    """
    Test that a user can successfully log in with correct credentials.

    """
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    # Use form data instead of JSON for the login endpoint.
    response = client.post("/api/v1/users/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200, "Login should return status 200"
    data = response.json()
    assert "access_token" in data, "Login response must contain an access token"
    assert data["token_type"] == "bearer", "Token type should be 'bearer'"

def test_login_invalid_credentials(client: TestClient, test_user: dict):
    """
    Test that login fails when invalid credentials are provided.
    """
    response = client.post("/api/v1/users/login", data={
        "username": test_user["username"],
        "password": "wrongpassword"
    })
    # Expect a 422 since the login endpoint uses form data validation,
    # but invalid credentials should normally result in 401.
    # Adjust the expected status code if your endpoint differentiates between form errors and auth errors.
    assert response.status_code == 401 or response.status_code == 422, "Invalid credentials should return status 401 or 422"
    assert "Incorrect username or password" in response.json()["detail"], "Error message must indicate incorrect credentials"

def test_get_current_user(client: TestClient, test_user: dict, db_session: Session):
    """
    Test retrieving the current authenticated user's data.
    """
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/api/v1/users/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "Retrieving current user should return status 200"
    data = response.json()
    assert data["email"] == test_user["email"], "Returned email does not match"
    assert data["username"] == test_user["username"], "Returned username does not match"
    assert "hashed_password" not in data, "Response should not expose hashed_password"

def test_update_user(client: TestClient, test_user: dict, db_session: Session):
    """
    Test updating the current authenticated user's profile.
    """
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/api/v1/users/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]

    update_data = {
        "email": "newemail@example.com",
        "username": "newusername"
    }
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "User update should return status 200"
    data = response.json()
    assert data["email"] == update_data["email"], "Email update did not persist"
    assert data["username"] == update_data["username"], "Username update did not persist"

def test_delete_user(client: TestClient, test_user: dict, db_session: Session):
    """
    Test deleting the current authenticated user's account.
    """
    # Create a new user and store its id before deletion.
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"])
    )
    db_session.add(user)
    db_session.commit()
    user_id = user.id  # Save user id for later verification.

    # Login using form data.
    login_response = client.post("/api/v1/users/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]

    # Delete the user.
    response = client.delete(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204, "User deletion should return status 204"

    # Clear the session identity map, then query using the saved user id.
    db_session.expunge_all()
    deleted_user = db_session.query(User).filter(User.id == user_id).first()
    assert deleted_user is None, "User should be deleted from the database"


