import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import Base, engine
from auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from models.user import User

@pytest.fixture(autouse=True)
def setup_tables():
    """
    Automatically create the database tables before each test and drop them afterwards.
    This fixture ensures that the tests run with a fresh schema.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_verify_password():
    """
    Ensure that verify_password correctly validates a valid password
    and rejects an invalid one.
    """
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True, "Failed to verify correct password"
    assert verify_password("wrongpassword", hashed_password) is False, "Incorrect password erroneously verified"

def test_create_access_token():
    """
    Test that create_access_token returns a non-empty JWT token as a string.
    """
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str), "Token is not a string"
    assert len(token) > 0, "Token is empty"

@pytest.mark.asyncio
async def test_get_current_user_valid_token(db_session: Session):
    """
    Steps:
      1. Create a test user and add it to the database.
      2. Generate a valid token for the test user.
      3. Use get_current_user to verify the token returns the correct user.
    """
    # Create a test user.
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    db_session.commit()

    # Generate a valid token for the test user.
    token = create_access_token({"sub": "testuser"})
    
    # Retrieve the user using the valid token.
    current_user = await get_current_user(token, db_session)
    assert current_user.username == "testuser", "Returned username does not match expected value"
    assert current_user.email == "test@example.com", "Returned email does not match expected value"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session: Session):
    """
    Verify that get_current_user raises an HTTPException for an invalid token.
    """
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", db_session)
    assert exc_info.value.status_code == 401, "Expected HTTP 401 Unauthorized for invalid token"

@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(db_session: Session):
    """
    Verify that get_current_user raises an HTTPException when the token refers to a nonexistent user.
    """
    # Generate a token for a user that does not exist.
    token = create_access_token({"sub": "nonexistent"})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, db_session)
    assert exc_info.value.status_code == 401, "Expected HTTP 401 Unauthorized for nonexistent user"
