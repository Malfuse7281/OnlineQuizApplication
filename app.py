
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "quiz_app_secret_key_2026"

def connect_db():
    return sqlite3.connect("quiz.db")

def create_db():
    con = connect_db()
    con.execute("""CREATE TABLE IF NOT EXISTS questions
    (id INTEGER PRIMARY KEY, question TEXT,
    op1 TEXT, op2 TEXT, op3 TEXT, op4 TEXT, answer TEXT)""")

    con.execute("""CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, email TEXT UNIQUE, password TEXT)""")

    count = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    if count == 0:
        data = [
            ("Capital of India?", "Mumbai", "Delhi", "Chennai", "Kolkata", "Delhi"),
            ("Which is a programming language?", "HTML", "CSS", "Python", "SQL", "Python"),
            ("5 + 5 = ?", "8", "10", "15", "20", "10"),
            ("Which is a database?", "Python", "SQLite", "HTML", "CSS", "SQLite"),
            ("Who developed Python?", "James Gosling", "Guido van Rossum", "Dennis Ritchie", "Bill Gates", "Guido van Rossum")
        ]

        con.executemany("""INSERT INTO questions
        (question,op1,op2,op3,op4,answer)
        VALUES (?,?,?,?,?,?)""", data)

    con.execute("""CREATE TABLE IF NOT EXISTS results
    (id INTEGER PRIMARY KEY, username TEXT, score INTEGER, total INTEGER)""")

    con.commit()
    con.close()

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("quiz"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = connect_db()
        try:
            con.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                        (name, email, generate_password_hash(password)))
            con.commit()
            con.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            con.close()
            return render_template("register.html",
                                  error="Email already registered!")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = connect_db()
        user = con.execute("SELECT * FROM users WHERE email=?",
                           (email,)).fetchone()
        con.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            return redirect(url_for("quiz"))

        return render_template("login.html", error="Invalid email or password!")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/quiz", methods=["GET"])
def quiz():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    con = connect_db()
    questions = con.execute("SELECT * FROM questions").fetchall()
    con.close()
    return render_template("quiz.html", questions=questions,
                           name=session["name"])

@app.route("/result", methods=["POST"])
def result():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    name = session["name"]
    con = connect_db()
    questions = con.execute("SELECT * FROM questions").fetchall()

    score = 0
    for q in questions:
        if request.form.get(str(q[0])) == q[6]:
            score += 1

    total = len(questions)

    con.execute("INSERT INTO results (username,score,total) VALUES (?,?,?)",
                (name,score,total))
    con.commit()
    con.close()

    return render_template("result.html", name=name, score=score, total=total)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)
