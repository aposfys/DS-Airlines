from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to DS Airlines API"}

def test_auth_register():
    # Since we don't have a mocked DB in this simple setup, this might fail if DB is not running.
    # But we can test validation.
    response = client.post("/api/auth/register", json={
        "email": "invalid-email",
        "username": "test",
        "fullname": "Test User",
        "password": "pwd",
        "passport_num": "123"
    })
    assert response.status_code == 422 # Validation Error
