import pytest
import sys
import os
from flask import session
from bson.objectid import ObjectId

# Ensure the app path is set correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your Flask app and mongo object
from app import app, mongo  # adjust this if your app is in another file like `main.py`

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

def test_complete_task(client):
    client.post("/signup", data={
        "username": "completeuser",
        "email": "complete@example.com",
        "password": "pass",
        "confirm_password": "pass"
    })
    client.post("/login", data={
        "identifier": "completeuser",
        "password": "pass"
    })
    client.post("/dashboard", data={"task": "Complete Me", "category": "Work"})
    task = mongo.db.tasks.find_one({"task_text": "Complete Me"})
    assert task

    response = client.get(f"/complete_task/{task['_id']}", follow_redirects=True)
    updated_task = mongo.db.tasks.find_one({"_id": task["_id"]})
    assert updated_task["completed"] is True

def test_delete_task(client):
    client.post("/signup", data={
        "username": "deleteuser",
        "email": "delete@example.com",
        "password": "pass",
        "confirm_password": "pass"
    })
    client.post("/login", data={
        "identifier": "deleteuser",
        "password": "pass"
    })
    client.post("/dashboard", data={"task": "To Delete", "category": "Work"})
    task = mongo.db.tasks.find_one({"task_text": "To Delete"})
    assert task

    response = client.get(f"/delete_task/{task['_id']}", follow_redirects=True)
    assert b"To Delete" not in response.data

def test_add_and_complete_subtask(client):
    client.post("/signup", data={
        "username": "subtaskuser",
        "email": "subtask@example.com",
        "password": "pass",
        "confirm_password": "pass"
    })
    client.post("/login", data={
        "identifier": "subtaskuser",
        "password": "pass"
    })
    client.post("/dashboard", data={"task": "Main Task", "category": "Work"})
    task = mongo.db.tasks.find_one({"task_text": "Main Task"})

    client.post(f"/add_subtask/{task['_id']}", data={"subtask": "Test Subtask"})
    task = mongo.db.tasks.find_one({"_id": task["_id"]})
    subtask = next((s for s in task["subtasks"] if s["text"] == "Test Subtask"), None)
    assert subtask is not None

    client.get(f"/complete_subtask/{subtask['_id']}", follow_redirects=True)
    task = mongo.db.tasks.find_one({"_id": task["_id"]})
    updated_subtask = next(s for s in task["subtasks"] if s["_id"] == subtask["_id"])
    assert updated_subtask["completed"] is True
