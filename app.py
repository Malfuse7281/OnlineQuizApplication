
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def connect_db():
    return sqlite3.connect("quiz.db")

def create_db():
    con = connect_db()
    con.execute("""CREATE TABLE IF NOT EXISTS questions
    (id INTEGER PRIMARY KEY, question TEXT,
    op1 TEXT, op2 TEXT, op3 TEXT, op4 TEXT, answer TEXT)""")

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

    con.commit()
    con.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/quiz", methods=["POST"])
def quiz():
    name = request.form["username"]
    con = connect_db()
    questions = con.execute("SELECT * FROM questions").fetchall()
    con.close()
    return render_template("quiz.html", questions=questions, name=name)

@app.route("/result", methods=["POST"])
def result():
    name = request.form["username"]
    con = connect_db()
    questions = con.execute("SELECT * FROM questions").fetchall()

    score = 0
    for q in questions:
        if request.form.get(str(q[0])) == q[6]:
            score += 1

    total = len(questions)

    con.execute("CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, username TEXT, score INTEGER, total INTEGER)")
    con.execute("INSERT INTO results (username,score,total) VALUES (?,?,?)",
                (name,score,total))
    con.commit()
    con.close()

    return render_template("result.html", name=name, score=score, total=total)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)
