from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import datetime
import pytz
import os

# Import models
from models.user_model import UserModel
from models.task_model import TaskModel

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Ensure SECRET_KEY is set in your .env file

# MongoDB config
app.config["MONGO_URI"] = os.getenv("MONGO_URI")  # Set MONGO_URI in .env
mongo = PyMongo(app)
from app import routes
__all__ = ["app", "mongo"]

# Timezone setup
app.jinja_env.globals["pytz"] = pytz

# Initialize models
user_model = UserModel(mongo)
task_model = TaskModel(mongo)

# Format user's created_at field for display
def format_user_created_at(user):
    timezone_kolkata = pytz.timezone("Asia/Kolkata")
    created_at = user.get("created_at")
    if created_at:
        if created_at.tzinfo is None:
            created_at = pytz.utc.localize(created_at)
        return created_at.astimezone(timezone_kolkata).strftime("%Y-%m-%d %I:%M %p")
    return "Not available"

# -------------------------
# 📌 Routes
# -------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

# -------- User Authentication --------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signup"))

        if user_model.find_by_email(email):
            flash("Email already exists!", "error")
            return redirect(url_for("signup"))

        user_model.create_user(username, email, password)
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["identifier"].strip().lower()
        password = request.form["password"]

        user = None
        if "@" in identifier:
            user = user_model.find_by_email(identifier.lower())
        else:
            user = user_model.find_by_username(identifier.lower())

        if user and user_model.verify_user(identifier, password):
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username/email or password", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# -------- Dashboard --------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    selected_category = request.args.get("category")
    timezone_kolkata = pytz.timezone("Asia/Kolkata")

    if request.method == "POST":
        task_text = request.form["task"].strip()
        end_time_input = request.form.get("end_time")
        priority = request.form.get("priority", "Medium")
        category = request.form.get("category", "Others")

        end_time = None
        if end_time_input:
            try:
                end_time = timezone_kolkata.localize(datetime.strptime(end_time_input, "%Y-%m-%dT%H:%M"))
            except ValueError:
                flash("Invalid date format for end time.", "error")
                return redirect(url_for("dashboard"))

        task_model.add_task(
            username=username,
            task_text=task_text,
            end_time=end_time,
            priority=priority,
            category=category
        )
        return redirect(url_for("dashboard"))

    tasks = task_model.get_tasks(username, category=selected_category)
    all_tasks = task_model.get_tasks(username)
    categories = sorted(set(task.get("category", "Others") for task in all_tasks))
    completion = task_model.get_completion_percentage(tasks)

    category_completion = {}
    for cat in categories:
        cat_tasks = [task for task in all_tasks if task.get("category") == cat]
        completed = len([task for task in cat_tasks if task.get("completed")])
        total = len(cat_tasks)
        percent = round((completed / total) * 100, 2) if total > 0 else 0
        category_completion[cat] = percent

    for task in tasks:
        for time_field in ["start_time", "end_time"]:
            dt = task.get(time_field)
            if dt:
                if dt.tzinfo is None:
                    dt = pytz.utc.localize(dt)
                task[f"{time_field}_str"] = dt.astimezone(timezone_kolkata).strftime("%Y-%m-%d %I:%M %p")
            else:
                task[f"{time_field}_str"] = "Not set" if time_field != "start_time" else "Not available"

    user = user_model.find_by_username(username)
    created_at_str = format_user_created_at(user)

    return render_template(
        "dashboard.html",
        tasks=tasks,
        categories=categories,
        selected_category=selected_category,
        completion_percentage=completion,
        category_completion=category_completion,
        created_at=created_at_str
    )

# -------- Task Management --------

@app.route("/complete_task/<task_id>")
def complete_task(task_id):
    task_model.complete_task(task_id)
    return redirect(url_for("dashboard"))

@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    task_model.delete_task(task_id)
    return redirect(url_for("dashboard"))

# -------- Subtask Management --------

@app.route("/add_subtask/<task_id>", methods=["POST"])
def add_subtask(task_id):
    subtask_text = request.form.get("subtask", "").strip()
    if not subtask_text:
        flash("Subtask cannot be empty!", "error")
        return redirect(url_for("dashboard"))

    task_model.add_subtask(task_id, subtask_text)
    return redirect(url_for("dashboard"))

@app.route("/complete_subtask/<subtask_id>")
def complete_subtask(subtask_id):
    task_model.complete_subtask(subtask_id)
    return redirect(url_for("dashboard"))

@app.route("/delete_subtask/<subtask_id>")
def delete_subtask(subtask_id):
    task_model.delete_subtask(subtask_id)
    return redirect(url_for("dashboard"))

# -------- Timezone Context --------

@app.context_processor
def inject_timezones():
    return {"timezone": pytz.timezone("Asia/Kolkata")}

# -------------------------
# 🚀 Run the App
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
