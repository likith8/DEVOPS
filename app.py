from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

from models.user_model import UserModel
from models.task_model import TaskModel

# Load environment variables from .env file
load_dotenv()

# Create the Flask app
app = Flask(__name__)

# Set the secret key using the environment variable from .env
app.secret_key = os.getenv("SECRET_KEY")

# Mongo URI setup with validation
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in the .env file or environment variables.")

# Debugging step: Print Mongo URI (for debugging only, remove in production)
print(f"Mongo URI: {mongo_uri}")

app.config["MONGO_URI"] = mongo_uri

# Initialize PyMongo and Models
mongo = PyMongo(app)

# Debugging step: Check MongoDB connection
try:
    print("Collections in DB:", mongo.db.list_collection_names())
    print("MongoDB connected successfully.")
except Exception as e:
    print("MongoDB connection failed:", e)
    raise

user_model = UserModel(mongo)
task_model = TaskModel(mongo)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for("signup"))

        if user_model.find_by_username(username):
            flash("Username already exists!")
            return redirect(url_for("signup"))

        user_model.create_user(username, password)
        flash("Signup successful! Please login.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if user_model.verify_user(username, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"
            return render_template("login.html", error=error)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    tasks = task_model.get_tasks(session["user"])
    completion = task_model.get_completion_percentage(tasks)

    return render_template("dashboard.html", tasks=tasks, completion_percentage=completion)

@app.route("/add", methods=["POST"])
def add_task():
    if "user" in session:
        task_text = request.form["task"]
        task_model.add_task(session["user"], task_text)
    return redirect(url_for("dashboard"))

@app.route("/complete/<task_id>")
def complete_task(task_id):
    task_model.complete_task(task_id)
    return redirect(url_for("dashboard"))

@app.route("/delete/<task_id>")
def delete_task(task_id):
    task_model.delete_task(task_id)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
