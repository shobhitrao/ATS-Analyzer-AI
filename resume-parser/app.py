from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

from parser import extract_text
from utils import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    detect_experience,
    missing_skills,
    resume_tips,
    ai_summary,
    section_scores,
    match_score
)

app = Flask(__name__)
app.secret_key = "ats_secret_key_2026"

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

    file = request.files["resume"]
    jd = request.form["jd"]

    if not file or file.filename == "":
        return "No file selected"

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    text = extract_text(path)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    experience = detect_experience(text)

    missing = missing_skills(text, jd)
    score = match_score(text, jd)

    tips = resume_tips(missing)
    summary = ai_summary(name, skills, score, missing)
    sections = section_scores(text)

    report = Report(
        username=session["user"],
        skills=", ".join(skills),
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
        skills=skills,
        missing=missing,
        score=score,
        tips=tips,
        summary=summary,
        sections=sections,
        jd_skills=extract_skills(jd)
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


# =========================
# VERIFY OTP
# =========================
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp = request.form["otp"]

        if otp == session.get("otp"):
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
        user = User.query.filter_by(username=username).first()

        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()

        session.pop("otp", None)
        session.pop("reset_user", None)

        return redirect("/login")

    return render_template("reset_password.html")


# =========================
# CHANGE PASSWORD
# =========================
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if not is_logged_in():
        return redirect("/login")

    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]

        user = User.query.filter_by(username=session["user"]).first()

        if user and check_password_hash(user.password, old):
            user.password = generate_password_hash(new)
            db.session.commit()
            return redirect("/")

        return "Wrong old password"

    return render_template("change_password.html")


# =========================
# DOWNLOAD REPORT
# =========================
@app.route("/download")
def download():
    if os.path.exists("report.pdf"):
        return send_file("report.pdf", as_attachment=True)

    return "PDF not found"


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)