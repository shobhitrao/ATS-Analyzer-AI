import os
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

import os
import time

from parser import extract_text

from utils import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    advanced_skills,
    detect_experience,
    resume_tips,
    ai_summary,
    section_scores,
    match_score,
    missing_skills
)

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)

app.secret_key = "ats_secret_key_2026"

app.permanent_session_lifetime = timedelta(minutes=30)

# =========================
# DATABASE
# =========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ats_analyzer.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# UPLOAD FOLDER
# =========================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# MODELS
# =========================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )


class Report(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(120))

    skills = db.Column(db.Text)

    score = db.Column(db.Integer)


with app.app_context():
    db.create_all()

# =========================
# LOGIN CHECK
# =========================

def is_logged_in():

    return "user" in session

# =========================
# HOME
# =========================

@app.route("/")
def home():

    if not is_logged_in():
        return redirect("/login")

    return render_template("index.html")

# =========================
# SIGNUP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()

        email = request.form["email"].strip()

        password = request.form["password"]

        existing = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing:
            return "Username or Email already exists"

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)

        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session.permanent = True

            session["user"] = username

            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================
# UPLOAD + ANALYZE
# =========================

@app.route("/upload", methods=["POST"])
def upload():

    if not is_logged_in():
        return redirect("/login")

    if "resume" not in request.files:
        return "No file selected"

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected"

    # =========================
    # SAVE FILE
    # =========================

    filename = (
        str(int(time.time())) +
        "_" +
        secure_filename(file.filename)
    )

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    # =========================
    # EXTRACT TEXT
    # =========================

    text = extract_text(filepath)

    if not text:
        return "Could not extract resume text"

    # =========================
    # BASIC INFO
    # =========================

    name = extract_name(text)

    email = extract_email(text)

    phone = extract_phone(text)

    experience = detect_experience(text)

    # =========================
    # SKILLS
    # =========================

    skills = advanced_skills(text)

    # =========================
    # JOB DESCRIPTION SKILLS
    # =========================

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

    # =========================
    # SECTION SCORES
    # =========================

    sections = section_scores(text)

    # =========================
    # JD MATCH SCORE
    # =========================

    jd_match_score = match_score(
        text,
        jd_text
    )

    # =========================
    # FINAL ATS SCORE
    # =========================

    WEIGHTS = {

        "skills": 0.35,

        "experience": 0.25,

        "projects": 0.20,

        "education": 0.10,

        "jd_match": 0.10
    }

    final_score = (

        sections["Skills"] * WEIGHTS["skills"] +

        sections["Experience"] * WEIGHTS["experience"] +

        sections["Projects"] * WEIGHTS["projects"] +

        sections["Education"] * WEIGHTS["education"] +

        jd_match_score * WEIGHTS["jd_match"]
    )

    final_score = round(final_score)

    # =========================
    # MISSING SKILLS
    # =========================

    missing = missing_skills(
        skills,
        jd_skills
    )

    # =========================
    # DISPLAY TEXT
    # =========================

    skills_text = (
        ", ".join(skills)
        if skills else
        "No Skills Found"
    )

    missing_text = (
        ", ".join(missing)
        if missing else
        "No Missing Skills 🎉"
    )

    jd_text_show = ", ".join(jd_skills)

    # =========================
    # TIPS + SUMMARY
    # =========================

    tips = resume_tips(missing)

    summary = ai_summary(
        name,
        skills,
        final_score,
        missing
    )

    # =========================
    # SAVE REPORT
    # =========================

    report = Report(

        username=session["user"],

        skills=skills_text,

        score=final_score
    )

    db.session.add(report)

    db.session.commit()

    # =========================
    # RESULT PAGE
    # =========================

    return render_template(

        "result.html",

        name=name,

        email=email,

        phone=phone,

        experience=experience,

        skills=skills_text,

        missing=missing_text,

        score=final_score,

        tips=tips,

        summary=summary,

        jd_skills=jd_text_show,

        sections=sections
    )

# =========================
# HISTORY
# =========================

@app.route("/history")
def history():

    if not is_logged_in():
        return redirect("/login")

    reports = Report.query.filter_by(
        username=session["user"]
    ).all()

    return render_template(
        "history.html",
        reports=reports
    )

# =========================
# DELETE REPORT
# =========================

@app.route("/delete_report/<int:id>")
def delete_report(id):

    if not is_logged_in():
        return redirect("/login")

    report = Report.query.get(id)

    if report:

        db.session.delete(report)

        db.session.commit()

    return redirect("/history")

# =========================
# DOWNLOAD REPORT
# =========================

@app.route("/download")
def download():

    pdf_path = "report.pdf"

    if os.path.exists(pdf_path):

        return send_file(
            pdf_path,
            as_attachment=True
        )

    return "PDF not found"

# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )