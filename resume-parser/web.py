from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
import time

from parser import extract_text
from utils import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    advanced_skills,
    match_score,
    detect_experience,
    missing_skills,
    resume_tips,
    ai_summary,
    section_scores
)

app = Flask(__name__)
app.secret_key = "ats_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///newdb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    score = db.Column(db.String(20))
    skills = db.Column(db.Text)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    session["user"] = "demo_user"
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        return "No File"

    file = request.files["resume"]

    filename = str(int(time.time())) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    text = extract_text(filepath)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    experience = detect_experience(text)

    skills = advanced_skills(text)

    # USER JD INPUT
    jd = request.form.get("jd", "").strip()

    # Default JD if blank
    if not jd:
        jd = """
        Looking for Python Developer with
        React, SQL, HTML, CSS, Git,
        AWS, Django, Docker,
        Machine Learning
        """

    jd_skills = extract_skills(jd)

    # Force fallback if extractor empty
    if not jd_skills:
        jd_skills = [
            "python", "react", "sql", "html",
            "css", "git", "aws", "django",
            "docker"
        ]

    score = match_score(text, jd)
    missing = missing_skills(skills, jd_skills)

    new_report = Report(
        username="demo_user",
        score=str(score),
        skills=", ".join(skills)
    )

    db.session.add(new_report)
    db.session.commit()

    tips = resume_tips(missing)
    summary = ai_summary(name, skills, score, missing)

    return render_template(
        "result.html",
        name=name,
        email=email,
        phone=phone,
        experience=experience,
        skills=skills,
        score=score,
        tips=tips,
        missing=missing,
        summary=summary,
        jd_skills=jd_skills,
        sections=section_scores(skills, text)
    )


if __name__ == "__main__":
    app.run(debug=True)