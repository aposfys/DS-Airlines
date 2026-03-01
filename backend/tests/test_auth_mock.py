import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.auth import get_password_hash, verify_password

# Test password hashing independently
def test_password_hashing():
    password = "securepassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

@pytest.mark.asyncio
async def test_register_user_mock():
    # Mock return values
    mock_find_one = AsyncMock(return_value=None)
    mock_insert_one = AsyncMock()
    mock_id = ObjectId()
    mock_insert_one.return_value.inserted_id = mock_id
    
    # We patch 'app.routers.auth.db'
    with patch("app.routers.auth.db", new_callable=MagicMock) as mock_db:
        # Configure find_one
        mock_db.users.find_one = AsyncMock(side_effect=[
            None, # First check: email
            None, # Second check: username
            {"_id": mock_id, "email": "test@example.com", "username": "testuser", "fullname": "Test User", "password": "hashed_pw"} # Third check: after insert
        ])
        
        # Configure insert_one
        mock_db.users.insert_one = mock_insert_one
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/auth/register", json={
                "fullname": "Test User",
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "passport_num": "A1234567"
            })
        
        # Debugging output if needed
        if response.status_code != 200:
            print(response.json())
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        # Check _id, as FastAPI uses alias by default
        assert data["_id"] == str(mock_id)

@pytest.mark.asyncio
async def test_login_mock():
    # Helper to hash password for mock user
    hashed_pw = get_password_hash("password123")
    mock_id = ObjectId()
    mock_user = {
        "_id": mock_id,
        "email": "test@example.com",
        "username": "testuser",
        "fullname": "Test User",
        "password": hashed_pw
    }
    
    with patch("app.routers.auth.db", new_callable=MagicMock) as mock_db:
        mock_db.users.find_one = AsyncMock(return_value=mock_user)
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/auth/login", json={
                "username": "testuser",
                "password": "password123"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_register_existing_email_mock():
    with patch("app.routers.auth.db", new_callable=MagicMock) as mock_db:
        mock_db.users.find_one = AsyncMock(return_value={"email": "test@example.com"})
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/auth/register", json={
                "fullname": "Test User",
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "passport_num": "A1234567"
            })
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"
