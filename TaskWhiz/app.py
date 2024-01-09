from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///task.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    # Render the index page with tasks
    # What I wrote in the task.db to create the users and tasks databases
    # CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL)
    # CREATE TABLE tasks (id INTEGER, user_id INTEGER, task TEXT, priority TEXT, day_of_week TEXT, PRIMARY KEY(id), FOREIGN KEY(user_id) REFERENCES users(id));
    todo = []
    user_id = session["user_id"]
    results = db.execute("SELECT id, task, priority, day_of_week FROM tasks WHERE user_id = ? ORDER BY CASE WHEN priority IS NULL THEN 1 ELSE 0 END, priority", user_id)
    for row in results:
        id = row["id"]
        task = row["task"]
        priority = row["priority"]
        day_of_week = row["day_of_week"]
        todo.append(row)
    return render_template("index.html", todo=todo)

@app.route("/add", methods=["POST"])
@login_required
def add():
    # Handle adding a task
    if request.method == "POST":
        user_id = session["user_id"]
        task = request.form.get("task")
        if not task:
            return redirect("/")
        else:
            priority = request.form.get("priority")
            db.execute("INSERT INTO tasks (user_id, task, priority) VALUES (?, ?, ?)", user_id, task, priority)
            return redirect("/")

@app.route("/complete", methods=["POST"])
@login_required
def complete():
    # Handle completing a task
    if request.method == "POST":
        task_id = request.form.get("task_id")
        db.execute("DELETE FROM tasks WHERE id = ?", task_id)
        return redirect("/")

@app.route("/save", methods=["POST"])
@login_required
def save():
    # Handle saving the task state
    if request.method == "POST":
        user_id = session["user_id"]
        data = request.get_json()  # Extract data from the request
        print("Received Data:", data)  # Log the received data
        task_name = data.get("taskName")
        day_of_week = data.get("dayOfWeek")
        # Update the day_of_week for the task in the database
        db.execute("UPDATE tasks SET day_of_week = ? WHERE user_id = ? AND task = ?",
                   day_of_week, user_id, task_name)
        return jsonify({"success": True})

@app.route("/load")
@login_required
def load():
    # Handle loading the task state
    user_id = session["user_id"]
    task_state = db.execute("SELECT day_of_week, task FROM tasks WHERE user_id = ?", user_id)
    return jsonify(task_state)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Handle user registration
    if request.method == "POST":
        # declaring variables
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return render_template("apology.html", apology="Must provide username")

        # Ensure password was submitted
        elif not password:
            return render_template("apology.html", apology="Must provide password")

        # Checking if the password and confirmation match
        if password == confirmation:
            # hashing the password
            hashed_password = generate_password_hash(password)
            # using a try-except statement to determine whether there was an error or not
            try:
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    username,
                    hashed_password,
                )
            except ValueError as e:
                if "UNIQUE constraint failed: users.username" in str(e):
                    return render_template("apology.html", apology="Username already taken")

            return redirect("/")
        else:
            return render_template("apology.html", apology="Passwords don't match")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Handle user login
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", apology="Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", apology="Must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("apology.html", apology="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Handle user logout
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
