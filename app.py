
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from database import db
import models
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config["SECRET_KEY"] = "quiz_app_secret_key_change_later"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

with app.app_context():
    db.create_all()


# -------------------- ACCESS CHECKS --------------------

def admin_required():
    return "user_id" in session and session.get("role") == "admin"


def student_required():
    return "user_id" in session and session.get("role") == "student"


# -------------------- PASSWORD RESET EMAIL --------------------

def send_reset_email(email, reset_link):
    mail_user = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    if not mail_user or not mail_password:
        print("\nPASSWORD RESET LINK:")
        print(reset_link)
        print()
        return

    msg = EmailMessage()
    msg["Subject"] = "Online Quiz - Password Reset"
    msg["From"] = mail_user
    msg["To"] = email
    msg.set_content(
        f"Click the link below to reset your password:\n\n"
        f"{reset_link}\n\n"
        "This link expires in 30 minutes."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(mail_user, mail_password)
        server.send_message(msg)


# -------------------- HOME --------------------

@app.route("/")
def home():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("student_dashboard"))

    return render_template("index.html")


# -------------------- REGISTRATION --------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if models.User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = models.User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="student"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------- LOGIN --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = models.User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session.clear()
            session["user_id"] = user.id
            session["name"] = user.name
            session["role"] = user.role
            return redirect(url_for("home"))

        flash("Invalid email or password.")

    return render_template("login.html")


# -------------------- LOGOUT --------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------- FORGOT PASSWORD --------------------

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = models.User.query.filter_by(email=email).first()

        if user:
            token = serializer.dumps(email, salt="password-reset")

            reset_link = url_for(
                "reset_password",
                token=token,
                _external=True
            )

            send_reset_email(email, reset_link)

        flash("If the account exists, a reset link has been generated.")
        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=1800
        )
    except (SignatureExpired, BadSignature):
        return render_template("reset_password.html", invalid=True)

    user = models.User.query.filter_by(email=email).first()

    if not user:
        return render_template("reset_password.html", invalid=True)

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("reset_password.html", invalid=False)

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return render_template("reset_password.html", invalid=False)

        user.password = generate_password_hash(password)
        db.session.commit()

        flash("Password reset successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("reset_password.html", invalid=False)


# -------------------- ADMIN DASHBOARD --------------------

@app.route("/admin_dashboard")
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("login"))

    subjects = models.Subject.query.order_by(
        models.Subject.id.desc()
    ).all()

    quizzes = models.Quiz.query.order_by(
        models.Quiz.id.desc()
    ).all()

    questions = models.Question.query.order_by(
        models.Question.id.desc()
    ).all()

    attempts = models.Attempt.query.order_by(
        models.Attempt.attempted_at.desc()
    ).all()

    return render_template(
        "admin_dashboard.html",
        subjects=subjects,
        quizzes=quizzes,
        questions=questions,
        attempts=attempts
    )


# -------------------- SUBJECT MANAGEMENT --------------------

@app.route("/add_subject", methods=["POST"])
def add_subject():
    if not admin_required():
        return redirect(url_for("login"))

    name = request.form["name"].strip()
    description = request.form.get("description", "").strip()

    if models.Subject.query.filter_by(name=name).first():
        flash("Subject already exists.")

    elif name:
        subject = models.Subject(
            name=name,
            description=description
        )

        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully.")

    return redirect(url_for("admin_dashboard"))


@app.route("/delete_subject/<int:id>")
def delete_subject(id):
    if not admin_required():
        return redirect(url_for("login"))

    subject = models.Subject.query.get_or_404(id)

    for quiz in subject.quizzes:
        for question in quiz.questions:
            db.session.delete(question)

        db.session.delete(quiz)

    db.session.delete(subject)
    db.session.commit()

    flash("Subject and its quizzes deleted.")
    return redirect(url_for("admin_dashboard"))


# -------------------- QUIZ MANAGEMENT --------------------

@app.route("/add_quiz", methods=["POST"])
def add_quiz():
    if not admin_required():
        return redirect(url_for("login"))

    title = request.form["title"].strip()
    subject_id = request.form["subject_id"]
    duration = request.form.get("duration", 10)

    if title:
        quiz = models.Quiz(
            title=title,
            subject_id=subject_id,
            duration=int(duration)
        )

        db.session.add(quiz)
        db.session.commit()
        flash("Quiz created successfully.")

    return redirect(url_for("admin_dashboard"))


@app.route("/delete_quiz/<int:id>")
def delete_quiz(id):
    if not admin_required():
        return redirect(url_for("login"))

    quiz = models.Quiz.query.get_or_404(id)

    for question in quiz.questions:
        db.session.delete(question)

    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz deleted.")
    return redirect(url_for("admin_dashboard"))


# -------------------- QUESTION MANAGEMENT --------------------

@app.route("/add_question", methods=["POST"])
def add_question():
    if not admin_required():
        return redirect(url_for("login"))

    question = models.Question(
        quiz_id=request.form["quiz_id"],
        question_text=request.form["question_text"].strip(),
        option1=request.form["option1"].strip(),
        option2=request.form["option2"].strip(),
        option3=request.form["option3"].strip(),
        option4=request.form["option4"].strip(),
        correct_option=request.form["correct_option"]
    )

    db.session.add(question)
    db.session.commit()

    flash("Question added.")
    return redirect(url_for("admin_dashboard"))


@app.route("/delete_question/<int:id>")
def delete_question(id):
    if not admin_required():
        return redirect(url_for("login"))

    question = models.Question.query.get_or_404(id)

    db.session.delete(question)
    db.session.commit()

    flash("Question deleted.")
    return redirect(url_for("admin_dashboard"))


# -------------------- STUDENT DASHBOARD --------------------

@app.route("/student_dashboard")
def student_dashboard():
    if not student_required():
        return redirect(url_for("login"))

    subjects = models.Subject.query.all()

    attempts = models.Attempt.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        models.Attempt.attempted_at.desc()
    ).all()

    return render_template(
        "student_dashboard.html",
        subjects=subjects,
        attempts=attempts
    )


# -------------------- TAKE QUIZ --------------------

@app.route("/quiz/<int:id>")
def take_quiz(id):
    if not student_required():
        return redirect(url_for("login"))

    quiz = models.Quiz.query.get_or_404(id)
    questions = quiz.questions

    if not questions:
        flash("This quiz has no questions yet.")
        return redirect(url_for("student_dashboard"))

    return render_template(
        "quiz.html",
        quiz=quiz,
        questions=questions
    )


# -------------------- SUBMIT QUIZ --------------------

@app.route("/submit_quiz/<int:id>", methods=["POST"])
def submit_quiz(id):
    if not student_required():
        return redirect(url_for("login"))

    quiz = models.Quiz.query.get_or_404(id)
    questions = quiz.questions
    score = 0

    for question in questions:
        selected = request.form.get(str(question.id))

        if selected == question.correct_option:
            score += 1

    total = len(questions)

    attempt = models.Attempt(
        user_id=session["user_id"],
        quiz_id=quiz.id,
        score=score,
        total=total
    )

    db.session.add(attempt)
    db.session.commit()

    return render_template(
        "result.html",
        quiz=quiz,
        score=score,
        total=total
    )


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    app.run(debug=True)
