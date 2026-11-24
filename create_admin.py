
from app import app
from database import db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    email = "admin@quiz.com"

    existing = User.query.filter_by(email=email).first()

    if existing:
        existing.role = "admin"
        existing.password = generate_password_hash("Admin@123")
    else:
        admin = User(
            name="Quiz Administrator",
            email=email,
            password=generate_password_hash("Admin@123"),
            role="admin"
        )
        db.session.add(admin)

    db.session.commit()
    print("Admin account created successfully!")
