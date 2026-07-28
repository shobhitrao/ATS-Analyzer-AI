import os
import time
import google.generativeai as genai

from flask import send_file
import os

from datetime import timedelta
from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
    missing_skills,
)

# =========================
# GEMINI CONFIG
# =========================

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "ats_secret_key_2026")
app.permanent_session_lifetime = timedelta(minutes=30)

# =========================
# DATABASE
# =========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ats_analyzer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# UPLOAD CONFIG
# =========================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =========================
# DATABASE MODELS
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

        existing = User.query.filter(
            (User.username == username)
            | (User.email == email)
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
# UPLOAD
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

    if not allowed_file(file.filename):
        return "Only PDF files are allowed."

    filename = (
        str(int(time.time()))
        + "_"
        + secure_filename(file.filename)
    )

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename,
    )

    file.save(filepath)

    text = extract_text(filepath)

    if not text:
        os.remove(filepath)
        return "Could not extract resume text"
    

    # Continue with:
    # name = extract_name(text)
    # email = extract_email(text)
    # phone = extract_phone(text)
    # ...

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
    # JOB DESCRIPTION
    # =========================

    jd_text = request.form.get("job_description", "").strip()

    if not jd_text:
        jd_text = """
Python
SQL
HTML
CSS
JavaScript
Git
Communication
Problem Solving
Team Work
"""

    jd_skills = extract_skills(jd_text)

    # =========================
    # SECTION SCORES
    # =========================

    sections = section_scores(text)

    # =========================
    # JD MATCH
    # =========================

    jd_match_score = match_score(text, jd_text)

    # =========================
    # PROFESSIONAL ATS SCORE
    # =========================

    skills_score = sections["Skills"]
    experience_score = sections["Experience"]
    project_score = sections["Projects"]
    education_score = sections["Education"]

    # Resume format score
    format_score = 0

    if name:
        format_score += 20

    if email:
        format_score += 20

    if phone:
        format_score += 20

    if len(text) > 500:
        format_score += 20

    if "education" in text.lower():
        format_score += 20

    # Contact score
    contact_score = 0

    if name:
        contact_score += 20

    if email:
        contact_score += 40

    if phone:
        contact_score += 40

    final_score = round(
        skills_score * 0.30 +
        jd_match_score * 0.25 +
        experience_score * 0.15 +
        project_score * 0.10 +
        education_score * 0.10 +
        format_score * 0.05 +
        contact_score * 0.05
    )

    final_score = max(0, min(100, final_score))

    if final_score >= 90:
        grade = "Excellent"
    elif final_score >= 80:
        grade = "Very Good"
    elif final_score >= 70:
        grade = "Good"
    elif final_score >= 60:
        grade = "Average"
    else:
        grade = "Needs Improvement"

        # =========================
        # MISSING SKILLS
        # =========================

        missing = missing_skills(skills, jd_skills)

        # =========================
        # DISPLAY TEXT
        # =========================

        skills_text = ", ".join(skills) if skills else "No Skills Found"

        missing_text = (
            ", ".join(missing)
            if missing
            else "No Missing Skills 🎉"
        )

        jd_text_show = jd_text

    # =========================
    # TIPS & SUMMARY
    # =========================

    tips = resume_tips(missing)

    summary = ai_summary(
        name,
        skills,
        final_score,
        missing,
    )

    # =========================
    # SAVE REPORT
    # =========================

    report = Report(
        username=session["user"],
        skills=skills_text,
        score=final_score,
    )

    db.session.add(report)
    db.session.commit()

    # =========================
    # GENERATE PDF REPORT
    # =========================

    generate_pdf_report(
        name=name,
        email=email,
        phone=phone,
        experience=experience,
        score=final_score,
        skills=skills_text,
        missing=missing_text,
        summary=summary,
        tips=tips,
    )

    # =========================
    # DELETE TEMP FILE
    # =========================

    if os.path.exists(filepath):
        os.remove(filepath)

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
        sections=sections,
    )
# =========================
# HISTORY
# =========================

@app.route("/history")
def history():

    if not is_logged_in():
        return redirect("/login")

    reports = (
        Report.query
        .filter_by(username=session["user"])
        .order_by(Report.id.desc())
        .all()
    )

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

    report = Report.query.filter_by(
        id=id,
        username=session["user"]
    ).first()

    if report:
        db.session.delete(report)
        db.session.commit()

    return redirect("/history")


# =========================
# PDF GENERATOR
# =========================

def generate_pdf_report(
    name,
    email,
    phone,
    experience,
    score,
    skills,
    missing,
    summary,
    tips,
):

    pdf_path = f"report_{session['user']}.pdf"

    c = canvas.Canvas(pdf_path, pagesize=A4)

    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y, "ATS Analyzer AI Report")

    y -= 40

    c.setFont("Helvetica", 12)

    data = [
        f"Name : {name}",
        f"Email : {email}",
        f"Phone : {phone}",
        f"Experience : {experience}",
        f"ATS Score : {score}%",
        "",
        "Skills:",
        skills,
        "",
        "Missing Skills:",
        missing,
        "",
        "AI Summary:",
    ]

    for line in data:
        c.drawString(50, y, line)
        y -= 20

    for line in summary.split("\n"):
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

        c.drawString(50, y, line)
        y -= 18

    y -= 15

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Resume Tips")
    y -= 20

    c.setFont("Helvetica", 12)

    for tip in tips:

        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

        c.drawString(60, y, "• " + tip)
        y -= 18

    c.save()

    return pdf_path

# =========================
# DOWNLOAD 
# =========================

@app.route("/download")
def download():

    if not is_logged_in():
        return redirect("/login")

    pdf_path = f"report_{session['user']}.pdf"

    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name="ATS_Analyzer_Report.pdf"
        )

    return "Report not found", 404




# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
    )