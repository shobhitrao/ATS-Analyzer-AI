from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import os
import time
from datetime import timedelta

from parser import extract_text
from utils import (
    extract_name,
    extract_email,
    extract_phone,
    advanced_skills,
    match_score,
    detect_experience,
    resume_tips,
    ai_summary,
    section_scores
)

app = Flask(__name__)
app.secret_key = "ats_secret_key"
app.permanent_session_lifetime = timedelta(minutes=2)

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
    session.permanent = True
    session["user"] = "demo_user"
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        return "No File Selected"

    file = request.files["resume"]

    filename = str(int(time.time())) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    text = extract_text(filepath)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    experience = detect_experience(text)

    # Resume skills
    skills = advanced_skills(text)

    # Static JD Skills
    jd_skills = [
        "Python",
        "React",
        "SQL",
        "HTML",
        "CSS",
        "Git",
        "AWS",
        "Django",
        "Docker",
        "Machine Learning"
    ]

    jd_text = " ".join(jd_skills)

    # ATS score
    score = match_score(text, jd_text)

    # Proper missing skills compare
    resume_lower = [x.lower().strip() for x in skills]
    missing = []

    for skill in jd_skills:
        if skill.lower().strip() not in resume_lower:
            missing.append(skill)

    # Suggestions + summary
    tips = resume_tips(missing)
    summary = ai_summary(name, skills, score, missing)

    # Convert for frontend
    skills_text = ", ".join(skills) if skills else "No Skills Found"
    jd_text_show = ", ".join(jd_skills)
    missing_text = ", ".join(missing) if missing else "No Missing Skills 🎉"

    # Save DB
    new_report = Report(
        username="demo_user",
        score=str(score),
        skills=skills_text
    )

    db.session.add(new_report)
    db.session.commit()

    return render_template(
        "result.html",
        name=name,
        email=email,
        phone=phone,
        experience=experience,
        skills=skills_text,
        score=score,
        tips=tips,
        missing=missing_text,
        summary=summary,
        jd_skills=jd_text_show,
        sections=section_scores(skills, text)
    )


if __name__ == "__main__":
    app.run(debug=True)