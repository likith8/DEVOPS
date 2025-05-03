import pytest
from flask import session
from bson.objectid import ObjectId
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, mongo

# ----------- Fixtures -----------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            # Clean DB before each test
            mongo.db.users.delete_many({})
            mongo.db.tasks.delete_many({})
        yield client

# ----------- Tests -----------

def test_home_redirect(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

def test_signup_and_login(client):
    # Sign up new user
    response = client.post("/signup", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass",
        "confirm_password": "testpass"
    }, follow_redirects=True)
    assert b"Signup successful!" in response.data

    # Login with email
    response = client.post("/login", data={
        "identifier": "test@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    assert b"dashboard" in response.data.lower()

def test_login_fail(client):
    response = client.post("/login", data={
        "identifier": "invalid@example.com",
        "password": "wrongpass"
    }, follow_redirects=True)
    assert b"Invalid username/email or password" in response.data

def test_dashboard_access_without_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

def test_add_task(client):
    # Sign up and login first
    client.post("/signup", data={
        "username": "taskuser",
        "email": "task@example.com",
        "password": "taskpass",
        "confirm_password": "taskpass"
    })
    client.post("/login", data={
        "identifier": "taskuser",
        "password": "taskpass"
    })

    response = client.post("/dashboard", data={
        "task": "Write Flask Tests",
        "category": "Testing",
        "priority": "High",
        "end_time": ""  # Optional
    }, follow_redirects=True)
    assert b"Write Flask Tests" in response.data
