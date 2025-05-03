import pytest
import sys
import os
from flask import session
from bs4 import BeautifulSoup
from bson.objectid import ObjectId

# Set path to project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app and mongo
from app import app, mongo  # Make sure mongo is defined in app.py

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        yield client

    with app.app_context():
        mongo.db.tasks.delete_many({})
        mongo.db.subtasks.delete_many({})

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
    task = mongo.db.tasks.find_one({"task": "To Delete"})
    assert task is not None
    response = client.get(f"/delete/{task['_id']}", follow_redirects=True)
    assert b"To Delete" not in response.data

def test_mark_task_completed(client):
    client.post("/add", data={"task": "Complete Me", "category": "Work"})
    task = mongo.db.tasks.find_one({"task": "Complete Me"})
    client.get(f"/complete/{task['_id']}", follow_redirects=True)
    updated_task = mongo.db.tasks.find_one({"_id": task["_id"]})
    assert updated_task.get("completed", False) is True

def test_add_subtask_to_existing(client):
    client.post("/add", data={"task": "Main Task", "category": "Work"})
    task = mongo.db.tasks.find_one({"task": "Main Task"})
    response = client.post(f"/add_subtask/{task['_id']}", data={"subtask_name": "Added Subtask"}, follow_redirects=True)
    assert b"Added Subtask" in response.data

def test_mark_subtask_completed(client):
    client.post("/add", data={"task": "Task with Sub", "category": "Work", "subtask": ["Check Me"]})
    task = mongo.db.tasks.find_one({"task": "Task with Sub"})
    subtask = mongo.db.subtasks.find_one({"task_id": str(task["_id"]), "name": "Check Me"})
    client.get(f"/toggle_subtask/{subtask['_id']}", follow_redirects=True)
    updated_sub = mongo.db.subtasks.find_one({"_id": subtask["_id"]})
    assert updated_sub.get("completed", False) is True

def test_delete_subtask(client):
    client.post("/add", data={"task": "Sub Delete Task", "category": "Work", "subtask": ["Temp Sub"]})
    task = mongo.db.tasks.find_one({"task": "Sub Delete Task"})
    subtask = mongo.db.subtasks.find_one({"task_id": str(task["_id"]), "name": "Temp Sub"})
    response = client.get(f"/delete_subtask/{subtask['_id']}", follow_redirects=True)
    assert b"Temp Sub" not in response.data

def test_filter_category(client):
    client.post("/add", data={"task": "Work Task", "category": "Work"})
    client.post("/add", data={"task": "Home Task", "category": "Home"})
    response = client.get("/?category=Home")
    assert b"Home Task" in response.data
    assert b"Work Task" not in response.data

def test_completion_percentage(client):
    client.post("/add", data={"task": "Progress Task", "category": "Work", "subtask": ["1", "2", "3"]})
    task = mongo.db.tasks.find_one({"task": "Progress Task"})
    subtask = mongo.db.subtasks.find_one({"task_id": str(task["_id"]), "name": "1"})
    client.get(f"/toggle_subtask/{subtask['_id']}", follow_redirects=True)
    updated_subs = list(mongo.db.subtasks.find({"task_id": str(task["_id"])}))
    assert any(st.get("completed", False) for st in updated_subs)

def test_invalid_task_name(client):
    response = client.post("/add", data={"task": "", "category": "Work"}, follow_redirects=True)
    assert b"Task name is required" in response.data or response.status_code == 400
