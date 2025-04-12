import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Add the project root (one level up) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import Base, get_db
from auth.auth import get_password_hash

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """
    Override the get_db dependency to use an in-memory SQLite database for testing.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db_session():
    """
    Create a new database session for a test.
    This fixture ensures that all database tables are created.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """
    Create a FastAPI test client with an initialized in-memory database.
    """
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    """
    Return test user data as a dictionary.
    """
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }

@pytest.fixture
def test_bookmark():
    """
    Return test bookmark data as a dictionary.
    """
    return {
        "title": "Test Bookmark",
        "url": "https://example.com",
        "description": "Test Description"
    }

@pytest.fixture
def auth_headers(client, test_user):
    """
    Create a test user and retrieve authentication headers for API requests.

    """
    # Register the test user
    response = client.post("/api/v1/users/register", json=test_user)
    assert response.status_code in (200, 201), "User registration failed"
    
    # Login using the test user's credentials
    response = client.post("/api/v1/users/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200, "User login failed"
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
