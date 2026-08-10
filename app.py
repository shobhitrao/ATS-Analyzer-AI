import os
import time

from flask import send_file
import os

from datetime import timedelta
from flask import Flask, render_template, request, redirect, session, send_file, flash
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
# APP CONFIG
# =========================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "ats_secret_key_2026")
app.permanent_session_lifetime = timedelta(minutes=30)

# =========================
# PASSWORD RESET SECURITY
# =========================

OTP_EXPIRY_SECONDS = 10 * 60
PASSWORD_MIN_LENGTH = 8

def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"

def send_reset_otp(recipient_email, otp):
    """
    Sends the reset OTP using SMTP environment variables.
    Required for production:
      SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", username)

    if not all([host, username, password, sender]):
        return False, "Email service is not configured. Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD and SMTP_FROM."

    msg = EmailMessage()
    msg["Subject"] = "ATS Analyzer AI - Password Reset OTP"
    msg["From"] = sender
    msg["To"] = recipient_email
    msg.set_content(
        f"Your ATS Analyzer AI password reset OTP is: {otp}\n\n"
        f"This OTP is valid for {OTP_EXPIRY_SECONDS // 60} minutes. "
        "If you did not request a password reset, ignore this email."
    )

    try:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        return True, None
    except Exception as exc:
        print(f"OTP email error: {exc}")
        return False, "Could not send OTP email. Please try again later."

def clear_reset_session():
    for key in (
        "reset_user_id",
        "reset_email",
        "reset_otp_hash",
        "reset_otp_expires",
        "reset_otp_attempts",
        "reset_verified",
    ):
        session.pop(key, None)


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
# FORGOT PASSWORD
# =========================

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()

        user = User.query.filter_by(
            username=username,
            email=email
        ).first()

        if not user:
            return render_template(
                "forgot_password.html",
                error="Username and email do not match."
            )

        otp = generate_otp()

        session["reset_user_id"] = user.id
        session["reset_email"] = user.email
        session["reset_otp_hash"] = generate_password_hash(otp)
        session["reset_otp_expires"] = time.time() + OTP_EXPIRY_SECONDS
        session["reset_otp_attempts"] = 0
        session["reset_verified"] = False

        sent, error = send_reset_otp(user.email, otp)

        if not sent:
            clear_reset_session()
            return render_template(
                "forgot_password.html",
                error=error
            )

        return redirect("/verify_otp")

    return render_template("forgot_password.html")


# =========================
# VERIFY OTP
# =========================

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if "reset_user_id" not in session:
        return redirect("/forgot_password")

    if time.time() > session.get("reset_otp_expires", 0):
        clear_reset_session()
        return render_template(
            "forgot_password.html",
            error="OTP expired. Please request a new OTP."
        )

    if request.method == "POST":
        otp = request.form.get("otp", "").strip()

        if not re.fullmatch(r"\d{6}", otp):
            return render_template(
                "verify_otp.html",
                error="Please enter a valid 6-digit OTP."
            )

        attempts = session.get("reset_otp_attempts", 0)

        if attempts >= 5:
            clear_reset_session()
            return render_template(
                "forgot_password.html",
                error="Too many incorrect OTP attempts. Please request a new OTP."
            )

        session["reset_otp_attempts"] = attempts + 1

        if not check_password_hash(session["reset_otp_hash"], otp):
            return render_template(
                "verify_otp.html",
                error=f"Incorrect OTP. Attempts remaining: {4 - attempts}."
            )

        session["reset_verified"] = True
        session.pop("reset_otp_hash", None)
        session.pop("reset_otp_attempts", None)

        return redirect("/reset_password")

    return render_template("verify_otp.html")


# =========================
# RESET PASSWORD
# =========================

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if not session.get("reset_verified"):
        return redirect("/forgot_password")

    user = db.session.get(User, session.get("reset_user_id"))

    if not user:
        clear_reset_session()
        return redirect("/forgot_password")

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < PASSWORD_MIN_LENGTH:
            return render_template(
                "reset_password.html",
                error=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
            )

        if password != confirm_password:
            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )

        user.password = generate_password_hash(password)
        db.session.commit()

        clear_reset_session()

        return render_template(
            "reset_password.html",
            success="Password updated successfully. You can now login."
        )

    return render_template("reset_password.html")


# =========================
# CHANGE PASSWORD
# =========================

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if not is_logged_in():
        return redirect("/login")

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    if not user:
        session.clear()
        return redirect("/login")

    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not check_password_hash(user.password, old_password):
            return render_template(
                "change_password.html",
                error="Old password is incorrect."
            )

        if len(new_password) < PASSWORD_MIN_LENGTH:
            return render_template(
                "change_password.html",
                error=f"New password must be at least {PASSWORD_MIN_LENGTH} characters long."
            )

        if new_password != confirm_password:
            return render_template(
                "change_password.html",
                error="New passwords do not match."
            )

        if check_password_hash(user.password, new_password):
            return render_template(
                "change_password.html",
                error="New password must be different from the old password."
            )

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return render_template(
            "change_password.html",
            success="Password changed successfully."
        )

    return render_template("change_password.html")



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

    # Format and contact are calculated by section_scores()
    # using real "found/not found" checks.
    format_score = sections["Format"]
    contact_score = sections["Contact"]

    final_score = round(
        skills_score * 0.30 +
        jd_match_score * 0.25 +
        experience_score * 0.15 +
        project_score * 0.10 +
        education_score * 0.10 +
        format_score * 0.05 +
        contact_score * 0.05
    )

    # Show the JD match in the dashboard without double-counting it.
    sections["JD Match"] = jd_match_score

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