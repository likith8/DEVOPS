import pytest
import sys
import os
from flask import session
from bs4 import BeautifulSoup

# Set path to project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app and db directly from app.py (since it's in the main folder)
from app import app, db  # Importing from app.py in the root directory
from task_model import Task, SubTask  # Import Task and SubTask from task_model.py

@pytest.fixture
def client():
    # Configure test settings
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.create_all()  # Create schema

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()  # Clean up DB

def test_home_redirect(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_add_task_basic(client):
    response = client.post("/add", data={"task": "Test Task", "category": "Work"}, follow_redirects=True)
    assert b"Test Task" in response.data

def test_add_task_with_subtasks(client):
    response = client.post("/add", data={ 
        "task": "Parent Task",
        "category": "Home",
        "subtask": ["Subtask 1", "Subtask 2"]
    }, follow_redirects=True)
    assert b"Parent Task" in response.data
    assert b"Subtask 1" in response.data
    assert b"Subtask 2" in response.data

def test_add_task_with_tags_and_priority(client):
    response = client.post("/add", data={
        "task": "Tagged Task",
        "category": "Study",
        "tags": "urgent,important",
        "priority": "High"
    }, follow_redirects=True)
    assert b"Tagged Task" in response.data
    assert b"urgent" in response.data
    assert b"important" in response.data

def test_delete_task(client):
    client.post("/add", data={"task": "To Delete", "category": "Misc"})
    task = Task.query.filter_by(task="To Delete").first()
    assert task is not None
    response = client.get(f"/delete/{task.id}", follow_redirects=True)
    assert b"To Delete" not in response.data

def test_mark_task_completed(client):
    client.post("/add", data={"task": "Complete Me", "category": "Work"})
    task = Task.query.filter_by(task="Complete Me").first()
    client.get(f"/complete/{task.id}", follow_redirects=True)
    updated_task = Task.query.get(task.id)
    assert updated_task.completed is True

def test_add_subtask_to_existing(client):
    client.post("/add", data={"task": "Main Task", "category": "Work"})
    task = Task.query.filter_by(task="Main Task").first()
    response = client.post(f"/add_subtask/{task.id}", data={"subtask_name": "Added Subtask"}, follow_redirects=True)
    assert b"Added Subtask" in response.data

def test_mark_subtask_completed(client):
    client.post("/add", data={"task": "Task with Sub", "category": "Work", "subtask": ["Check Me"]})
    task = Task.query.filter_by(task="Task with Sub").first()
    subtask = SubTask.query.filter_by(task_id=task.id, name="Check Me").first()
    client.get(f"/toggle_subtask/{subtask.id}", follow_redirects=True)
    updated_sub = SubTask.query.get(subtask.id)
    assert updated_sub.completed is True

def test_delete_subtask(client):
    client.post("/add", data={"task": "Sub Delete Task", "category": "Work", "subtask": ["Temp Sub"]})
    task = Task.query.filter_by(task="Sub Delete Task").first()
    subtask = SubTask.query.filter_by(task_id=task.id, name="Temp Sub").first()
    response = client.get(f"/delete_subtask/{subtask.id}", follow_redirects=True)
    assert b"Temp Sub" not in response.data

def test_filter_category(client):
    client.post("/add", data={"task": "Work Task", "category": "Work"})
    client.post("/add", data={"task": "Home Task", "category": "Home"})
    response = client.get("/?category=Home")
    assert b"Home Task" in response.data
    assert b"Work Task" not in response.data

def test_completion_percentage(client):
    client.post("/add", data={"task": "Progress Task", "category": "Work", "subtask": ["1", "2", "3"]})
    task = Task.query.filter_by(task="Progress Task").first()
    subtask = SubTask.query.filter_by(task_id=task.id, name="1").first()
    client.get(f"/toggle_subtask/{subtask.id}", follow_redirects=True)
    updated_subs = SubTask.query.filter_by(task_id=task.id).all()
    assert any(st.completed for st in updated_subs)

def test_invalid_task_name(client):
    response = client.post("/add", data={"task": "", "category": "Work"}, follow_redirects=True)
    assert b"Task name is required" in response.data or response.status_code == 400
