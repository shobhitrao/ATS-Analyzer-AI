from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect, send_file
from reportlab.pdfgen import canvas
import os
import time
import random
import smtplib

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from email.mime.text import MIMEText

from parser import extract_text
from app import (
    extract_name,
    extract_skills,
    match_score,
    resume_tips,
    ai_summary,
    section_scores,
    missing_skills,
)

from utils import detect_experience

# ===============================
# EXTRA SKILLS FUNCTION
# ===============================
def advanced_skills(text):
    skills = extract_skills(text)

    extra = [
        "python", "sql", "html", "css", "javascript",
        "react", "git", "github", "aws", "flask",
        "django", "pandas", "numpy"
    ]

    found = []

    for skill in extra:
        if skill.lower() in text.lower():
            found.append(skill)

    return list(set(skills + found))


# ===============================
# APP SETUP
# ===============================
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=10)
app.secret_key = "ATS Analyzer AI123"

EMAIL_ADDRESS = "shobhitrao.2005@gmail.com"
EMAIL_PASSWORD = "dmrd puhs glyz qnxj"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ATS Analyzer AI.db"
db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
report_data = {}
otp_store = {}

# ===============================
# DATABASE MODELS
# ===============================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(300))


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    score = db.Column(db.String(20))
    skills = db.Column(db.String(500))


@app.before_request
def session_timeout():
    session.permanent = True


# ===============================
# HOME PAGE
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


# ===============================
# LOGIN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ===============================
# SIGNUP
# ===============================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing = User.query.filter_by(username=username).first()

        if existing:
            return "Username already exists"

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")


# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")


# ===============================
# HISTORY
# ===============================
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    reports = Report.query.filter_by(username=session["user"]).all()

    return render_template("history.html", reports=reports)


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ===============================
# UPLOAD RESUME
# ===============================
@app.route("/upload", methods=["POST"])
def upload():

    global report_data

    if "user" not in session:
        return redirect("/login")

    file = request.files["resume"]
    jd = request.form.get("jd", "").strip()

    if file:

        filename = str(int(time.time())) + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        text = extract_text(filepath)

        name = extract_name(text)
        skills = advanced_skills(text)

        if jd:
            jd_skills = extract_skills(jd)
            score = match_score(text, jd)
            missing = missing_skills(skills, jd_skills)

        else:
            jd = """
            Looking for Python Developer with React, SQL,
            HTML, CSS, Git, AWS knowledge.
            """

            jd_skills = extract_skills(jd)
            score = match_score(text, jd)
            missing = missing_skills(skills, jd_skills)

        new_report = Report(
            username=session["user"],
            score=str(score),
            skills=", ".join(skills)
        )

        db.session.add(new_report)
        db.session.commit()

        report_data = {
            "name": name,
            "skills": skills,
            "score": score,
            "missing": missing
        }

        tips = resume_tips(missing)
        summary = ai_summary(name, skills, score, missing)

        return render_template(
            "result.html",
            name=name,
            skills=skills,
            score=score,
            tips=tips,
            missing=missing,
            summary=summary,
            jd_skills=jd_skills,
            sections=section_scores(skills, text)
        )

    return "No File Selected"


# ===============================
# DOWNLOAD PDF
# ===============================
@app.route("/download")
def download():

    file_path = "report.pdf"

    c = canvas.Canvas(file_path)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(160, 800, "ATS Analyzer AI Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, 750, "Name: " + str(report_data["name"]))
    c.drawString(50, 720, "Skills: " + ", ".join(report_data["skills"]))
    c.drawString(50, 690, "Score: " + str(report_data["score"]) + "%")
    c.drawString(50, 660, "Missing: " + ", ".join(report_data["missing"]))

    c.save()

    return send_file(file_path, as_attachment=True)


# ===============================
# RUN APP
# ===============================
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)