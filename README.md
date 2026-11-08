# Online Quiz Application

## Project Description

The Online Quiz Application is a simple web-based application developed using Python Flask and SQLite. It allows users to participate in quizzes, answer multiple-choice questions, and view their final scores.

The main purpose of this project is to provide a simple and user-friendly platform for conducting online quizzes.

## Technologies Used

- **Frontend:** HTML, CSS
- **Backend:** Python, Flask
- **Database:** SQLite
- **Code Editor:** Visual Studio Code

## Features

- Simple and user-friendly interface.
- Multiple-choice quiz questions.
- Four options for each question.
- Automatic score calculation.
- Displays final quiz results.
- Stores quiz questions in an SQLite database.

## Project Structure

```text
OnlineQuizApplication/
│
├── app.py
├── requirements.txt
├── quiz.db
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── quiz.html
│   └── result.html
│
└── static/
    └── style.css
```

Note: The database file and virtual environment may be excluded from the GitHub repository using `.gitignore`.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Malfuse7281/OnlineQuizApplication.git
```

### 2. Open the Project Folder

```bash
cd OnlineQuizApplication
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Required Packages

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open in Browser

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## How It Works

1. The user opens the quiz application.
2. The home page displays the quiz interface.
3. The user starts the quiz.
4. Multiple-choice questions are displayed.
5. The user selects answers and submits the quiz.
6. The application checks the answers and calculates the score.
7. The final result is displayed to the user.

## Learning Outcomes

- Understanding Python Flask framework.
- Learning basic frontend development using HTML and CSS.
- Understanding SQLite database operations.
- Connecting frontend pages with backend functionality.
- Learning how to create and run a simple web application.

## Author

**Syed Malfuse**

Integrated M.Tech – Software Engineering

VIT-AP University

## Project Status

Completed – Academic Mini Project