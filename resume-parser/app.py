from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
import time
import random

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
    match_score
)

app = Flask(__name__)
app.secret_key = "ats_secret_key_2026"
app.permanent_session_lifetime = timedelta(minutes=2)

# =========================
# DATABASE
# =========================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ats_analyzer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# MODELS
# =========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


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

        user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if user:
            return "Username or Email already exists"

        hashed = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed
        )

        db.session.add(new_user)
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

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
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
        return render_template("index.html", error="Please upload a resume")

    file = request.files["resume"]

    if file.filename == "":
        return render_template("index.html", error="Please select a file")

    jd_text_input = request.form.get("jd")

    if not jd_text_input or jd_text_input.strip() == "":
        return render_template("index.html", error="Job description cannot be empty")
    
    # File type validation
    if not file.filename.lower().endswith((".pdf", ".docx")):
        return render_template("index.html", error="Only PDF or DOCX files are allowed")
    

    filename = str(int(time.time())) + "_" + secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    text = extract_text(path)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    experience = detect_experience(text)

    # Resume skills
    skills = advanced_skills(text)

    known_skills = [
        # Programming Languages
        "python", "java", "c", "c++", "javascript", "typescript", "go", "ruby", "kotlin", "swift",

        # Web Development
        "html", "css", "react", "angular", "vue", "node", "express", "flask", "django",

        # Databases
        "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",

        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",

        # Data & AI
        "machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",

        # Tools & Others
        "git", "github", "linux", "bash", "rest api", "graphql", "microservices"
    ]

    jd_text_lower = jd_text_input.lower()

    jd_skills = []

    for skill in known_skills:
        if skill in jd_text_lower:
            jd_skills.append(skill)
    
    jd_text = jd_text_input

    # ATS Score
    score = match_score(text, jd_text)

    # Missing Skills Fix
    resume_lower = [x.lower().strip() for x in skills]
    jd_skills = [s.lower() for s in jd_skills]
    missing = []

    for skill in jd_skills:
        if skill.lower().strip() not in resume_lower:
            missing.append(skill)

    # Text for Frontend
    skills_text = ", ".join(skills) if skills else "No Skills Found"
    jd_text_show = ", ".join(jd_skills)
    missing_text = ", ".join(missing) if missing else "No Missing Skills 🎉"

    # Suggestions
    tips = resume_tips(missing)
    summary = ai_summary(name, skills, score, missing)

    # Save Report
    report = Report(
        username=session["user"],
        skills=skills_text,
        score=score
    )

    db.session.add(report)
    db.session.commit()

    return render_template(
        "result.html",
        name=name,
        email=email,
        phone=phone,
        experience=experience,
        skills=skills_text,
        missing=missing_text,
        score=score,
        tips=tips,
        summary=summary,
        jd_skills=jd_text_show,
        sections=section_scores(text)
    )


# =========================
# HISTORY
# =========================
@app.route("/history")
def history():
    if not is_logged_in():
        return redirect("/login")

    reports = Report.query.filter_by(username=session["user"]).all()
    return render_template("history.html", reports=reports)


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
    if os.path.exists("report.pdf"):
        return send_file("report.pdf", as_attachment=True)

    return "PDF not found"


# =========================
# FORGOT PASSWORD
# =========================
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        user = User.query.filter_by(
            username=username,
            email=email
        ).first()

        if user:
            otp = str(random.randint(1000, 9999))
            session["otp"] = otp
            session["reset_user"] = username
            return redirect("/verify_otp")

        return "User not found"

    return render_template("forgot_password.html")


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp = request.form["otp"]

        if otp == session.get("otp"):
            return redirect("/reset_password")

        return "Invalid OTP"

    return render_template("verify_otp.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form["password"]

        username = session.get("reset_user")
        user = User.query.filter_by(username=username).first()

        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()

        session.pop("otp", None)
        session.pop("reset_user", None)

        return redirect("/login")

    return render_template("reset_password.html")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)