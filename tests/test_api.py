import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.models.models import User, Project
from app.core.security import hash_password

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    if response.headers.get("content-type") == "application/json":
        assert response.json()["project"] == "DevForge"

def test_register_user_success():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "student@example.com",
            "password": "strongpassword123",
            "full_name": "Student Developer",
            "github_username": "studentdev"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "student@example.com"
    assert "id" in data

def test_register_duplicate_user():
    user_data = {
        "email": "Student@example.com",
        "password": "strongpassword123",
        "full_name": "Student Developer"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Should fail due to email normalization matching "student@example.com"
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"

def test_register_invalid_email():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "pw",
            "full_name": "Test"
        }
    )
    assert response.status_code == 422 # Pydantic validation error

def test_login_success():
    # Register first
    client.post(
        "/api/auth/register",
        json={"email": "login@test.com", "password": "password", "full_name": "Login Test"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "login@test.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password():
    client.post(
        "/api/auth/register",
        json={"email": "wrongpw@test.com", "password": "password", "full_name": "Test"}
    )
    
    response = client.post(
        "/api/auth/login",
        json={"email": "wrongpw@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_protected_me_endpoint():
    client.post(
        "/api/auth/register",
        json={"email": "me@test.com", "password": "password", "full_name": "Me Test"}
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": "me@test.com", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"

def test_create_project():
    client.post(
        "/api/auth/register",
        json={"email": "project@test.com", "password": "password", "full_name": "Project Test"}
    )
    login_response = client.post("/api/auth/login", json={"email": "project@test.com", "password": "password"})
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/api/projects/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "My Awesome Project",
            "tech_stack": "Python, FastAPI",
            "description": "Test description"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Awesome Project"
    assert data["status"] == "in_progress"

def test_project_ownership_isolation():
    # User 1
    client.post("/api/auth/register", json={"email": "user1@test.com", "password": "pw", "full_name": "U1"})
    t1 = client.post("/api/auth/login", json={"email": "user1@test.com", "password": "pw"}).json()["access_token"]
    
    # User 2
    client.post("/api/auth/register", json={"email": "user2@test.com", "password": "pw", "full_name": "U2"})
    t2 = client.post("/api/auth/login", json={"email": "user2@test.com", "password": "pw"}).json()["access_token"]
    
    # User 1 creates project
    p1 = client.post("/api/projects/", headers={"Authorization": f"Bearer {t1}"}, json={"title": "U1 Project", "tech_stack": "Python"}).json()
    project_id = p1["id"]
    
    # User 2 tries to access User 1's project
    response = client.get(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {t2}"})
    assert response.status_code == 404 # Isolated
    
    # User 2 tries to delete User 1's project
    del_response = client.delete(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {t2}"})
    assert del_response.status_code == 404

def test_update_profile():
    client.post(
        "/api/auth/register",
        json={"email": "update@test.com", "password": "password", "full_name": "Old Name", "github_username": "oldgit"}
    )
    login_response = client.post("/api/auth/login", json={"email": "update@test.com", "password": "password"})
    token = login_response.json()["access_token"]
    
    response = client.put(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "New Name", "github_username": "newgit"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["github_username"] == "newgit"

