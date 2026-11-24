# Online Quiz Application

## Project Overview
The Online Quiz Application is a web-based application developed using Python Flask that allows students to take subject-wise quizzes and administrators to manage quiz content.

## Technologies Used
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript

## Features
- Student registration and login
- Admin login
- Role-based dashboards
- Subject management
- Quiz creation and management
- MCQ question management
- Quiz timer
- Automatic score calculation
- Student quiz history
- Admin attempt monitoring

## Installation

1. Clone or download the project.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   `py -m venv venv`

4. Activate the environment:

   `.\venv\Scripts\Activate.ps1`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Create the admin account:

   `python create_admin.py`

7. Run the application:

   `python app.py`

8. Open `http://127.0.0.1:5000/` in your browser.

## Admin Account
Demo admin credentials are created locally using `create_admin.py`. Change the default password before deployment.

## Project Purpose
This project demonstrates web development, database management, user authentication, role-based access, quiz management and automated result calculation.
