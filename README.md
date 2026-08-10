# 🚀 ATS Analyzer AI

AI-powered Resume ATS Analyzer that analyzes resumes against Job Descriptions, detects skills, calculates ATS scores, identifies missing skills, and generates PDF reports.

🌐 **Live Demo:** https://ats-analyzer-ai-1.onrender.com

---

## ✨ Features

- ✅ Resume Upload (PDF)
- ✅ Resume Text Extraction
- ✅ OCR Support for Scanned PDFs
- ✅ ATS Score Analysis
- ✅ Section-wise ATS Scores
- ✅ Job Description Matching
- ✅ Skill Detection
- ✅ Missing Skill Detection
- ✅ Name, Email & Phone Extraction
- ✅ Experience Detection
- ✅ Project Detection
- ✅ Education Analysis
- ✅ Smart Resume Suggestions
- ✅ AI Summary
- ✅ PDF Report Generation
- ✅ Saved Reports / History
- ✅ Delete Reports
- ✅ User Signup & Login
- ✅ Forgot Password with OTP
- ✅ Reset Password
- ✅ Change Password
- ✅ Responsive Dashboard
- ✅ Render Deployment

---

## 🛠 Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy

### Frontend
- HTML5
- CSS3
- JavaScript
- Jinja2

### NLP & Resume Analysis
- spaCy
- Scikit-learn
- NLP-based skill extraction

### PDF Processing
- pdfplumber
- PyPDF2
- pytesseract
- pdf2image

### Database
- SQLite

### Tools & Deployment
- Git
- GitHub
- VS Code
- Render

---

## 📊 ATS Scoring

ATS Analyzer AI evaluates resumes using multiple sections:

| Section | Purpose |
|---|---|
| Skills | Technical skills detected in the resume |
| Experience | Work/internship experience |
| Projects | Practical projects and development work |
| Education | Educational information |
| Format | Resume structure and completeness |
| Contact | Email, phone and contact details |
| JD Match | Match between resume and Job Description |

The final ATS score is displayed through a visual score meter.

---

## 🔍 Job Description Matching

Users can enter a Job Description along with their resume.

The application analyzes the Job Description and compares it with the skills detected in the resume.

It provides:

- 🎯 JD Match Score
- ✅ Matched Skills
- ❌ Missing Skills
- 📊 Resume compatibility information

---

## 📄 Resume Parsing

The application supports PDF resume parsing using multiple extraction methods.

### Supported technologies

- pdfplumber
- PyPDF2
- OCR with Tesseract
- pdf2image

The application can use OCR as a fallback when normal PDF text extraction is not sufficient.

---

## 📑 PDF Reports

After analyzing a resume, users can generate a downloadable PDF report containing the resume analysis and ATS results.

Users can also save and manage previous reports through the History section.

---

## 🔐 Authentication

The application provides:

- User Registration
- User Login
- Logout
- Forgot Password
- OTP Verification
- Password Reset
- Change Password

User reports are associated with the logged-in account.

---

## 📸 Screenshots

Screenshots of the application can be added here.

### Resume Analysis Dashboard

_Add screenshot here_

### ATS Score & Section Scores

_Add screenshot here_

### Saved Reports

_Add screenshot here_

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/shobhitrao/ATS-Analyzer-AI.git
