from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import google.generativeai as genai
import os
import time
import random

genai.configure(api_key="YOUR_GEMINI_API_KEY")

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
# PDF REPORT GENERATOR
# =========================

def generate_pdf_report(
    name,
    email,
    phone,
    score,
    skills,
    missing,
    summary,
    ai_suggestions,
    interview_questions
):

    pdf = SimpleDocTemplate("report.pdf")

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "<b>ATS Resume Analysis Report</b>",
        styles['Title']
    )

    content.append(title)

    content.append(Spacer(1, 20))

    data = [

        f"<b>Name:</b> {name}",

        f"<b>Email:</b> {email}",

        f"<b>Phone:</b> {phone}",

        f"<b>ATS Score:</b> {score}%",

        f"<b>Skills:</b> {skills}",

        f"<b>Missing Skills:</b> {missing}",

        f"<b>Summary:</b> {summary}",

        f"<b>AI Suggestions:</b><br/>{ai_suggestions}",

        f"<b>Interview Questions:</b><br/>{interview_questions}"
    ]

    for item in data:

        para = Paragraph(item, styles['BodyText'])

        content.append(para)

        content.append(Spacer(1, 12))

    pdf.build(content)

# =========================
# AI SUGGESTIONS
# =========================

def generate_ai_suggestions(resume_text):

    try:

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are a professional ATS Resume Analyzer.

        Analyze this resume carefully.

        Give:
        1. Resume improvement suggestions
        2. Missing technical skills
        3. ATS optimization tips
        4. Resume formatting improvements
        5. Interview preparation advice

        Resume:
        {resume_text}
        """

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI Error: {str(e)}"

# =========================
# AI INTERVIEW QUESTIONS
# =========================

def generate_interview_questions(resume_text):

    try:

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Analyze this resume and generate:

        1. Technical interview questions
        2. HR interview questions
        3. Project viva questions

        Resume:
        {resume_text}
        """

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI Error: {str(e)}"

# =========================
# AI RESUME REWRITER
# =========================

def rewrite_resume(resume_text):

    try:

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Rewrite and improve this resume.

        Make it:
        - ATS Friendly
        - Professional
        - Recruiter Attractive

        Improve:
        1. Summary
        2. Projects
        3. Experience
        4. Skills

        Resume:
        {resume_text}
        """

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI Error: {str(e)}"

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

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session.permanent = True

            session["user"] = username

            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")

# =========================
# CHANGE PASSWORD
# =========================

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if not is_logged_in():
        return redirect("/login")

    if request.method == "POST":

        old_password = request.form["old_password"]

        new_password = request.form["new_password"]

        confirm_password = request.form["confirm_password"]

        user = User.query.filter_by(
            username=session["user"]
        ).first()

        if not check_password_hash(
            user.password,
            old_password
        ):
            return "Old password is incorrect"

        if new_password != confirm_password:
            return "Passwords do not match"

        user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        return "Password Changed Successfully ✅"

    return render_template(
        "change_password.html"
    )
    
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

        if not user:
            return "Invalid Username or Email"

        otp = str(random.randint(100000, 999999))

        session["reset_user"] = username
        session["reset_otp"] = otp

        print("OTP =", otp)

        return redirect("/verify_otp")

    return render_template("forgot_password.html")


# =========================
# VERIFY OTP
# =========================

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        otp = request.form["otp"]

        if otp == session.get("reset_otp"):
            return redirect("/reset_password")

        return "Invalid OTP"

    return render_template("verify_otp.html")


# =========================
# RESET PASSWORD
# =========================

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if request.method == "POST":

        new_password = request.form["password"]

        username = session.get("reset_user")

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:
            return "User Not Found"

        user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        session.pop("reset_user", None)
        session.pop("reset_otp", None)

        return redirect("/login")

    return render_template("reset_password.html")

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

    filename = (
        str(int(time.time())) +
        "_" +
        secure_filename(file.filename)
    )

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    text = extract_text(filepath)

    if not text:
        return "Could not extract resume text"

    name = extract_name(text)

    email = extract_email(text)

    phone = extract_phone(text)

    experience = detect_experience(text)

    skills = advanced_skills(text)

    jd_text = request.form["job_description"]

    jd_skills = advanced_skills(jd_text)

    sections = section_scores(text)

    jd_match_score = match_score(text, jd_text)

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

    missing = missing_skills(skills, jd_skills)

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

    jd_text_show = (
        ", ".join(jd_skills)
        if jd_skills else
        "No JD Skills Found"
    )

    tips = resume_tips(missing)

    summary = ai_summary(
        name,
        skills,
        final_score,
        missing
    )

    ai_suggestions = generate_ai_suggestions(text)

    interview_questions = generate_interview_questions(text)

    rewritten_resume = rewrite_resume(text)

    generate_pdf_report(
        name,
        email,
        phone,
        final_score,
        skills_text,
        missing_text,
        summary,
        ai_suggestions,
        interview_questions
    )

    report = Report(
        username=session["user"],
        skills=skills_text,
        score=final_score
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
        score=final_score,
        tips=tips,
        summary=summary,
        jd_skills=jd_text_show,
        sections=sections,
        ai_suggestions=ai_suggestions,
        interview_questions=interview_questions,
        rewritten_resume=rewritten_resume
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
# DOWNLOAD PDF
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

    app.run(debug=True)