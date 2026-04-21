import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from parser import extract_text

# ===============================
# NLP Model Load
# ===============================

def jd_suggestions(jd):
    tips = []

    jd_lower = jd.lower().strip()

    if not jd_lower:
        tips.append("Add a Job Description for better matching.")
        return tips

    if len(jd_lower) < 80:
        tips.append("Job Description is too short. Add more details.")

    if "experience" not in jd_lower:
        tips.append("Mention required experience years.")

    if "responsibilities" not in jd_lower:
        tips.append("Add responsibilities section.")

    if "skills" not in jd_lower:
        tips.append("Mention required technical skills clearly.")

    if "communication" not in jd_lower:
        tips.append("Add soft skills like communication/teamwork.")

    if not tips:
        tips.append("Excellent Job Description.")

    return tips

# ===============================
# 🧠 Skills Extract (NLP Based)
# ===============================
def extract_skills(text):

    skills_list = [
        "python", "java", "javascript", "c++", "react",
        "node", "express", "html", "css",
        "sql", "mongodb", "mysql",
        "git", "github", "pandas", "numpy",
        "aws", "docker", "kubernetes"
    ]

    found = []

    words = text.lower().split()

    for word in words:
        if word in skills_list:
            found.append(word)

    return list(set(found))

def extract_experience(text):
    if "fresher" in text.lower():
        return "Fresher"

    exp = re.findall(r'(\d+)\s+years?', text.lower())

    if exp:
        return exp[0] + " Years"

    return "Not Found"

def extract_education(text):
    education_keywords = [
        "b.tech", "btech", "b.e", "m.tech",
        "mba", "bca", "mca", "b.sc", "bcom"
    ]

    for edu in education_keywords:
        if edu in text.lower():
            return edu.upper()

    return "Not Found"


# ===============================
# 👤 Name Extract (NLP Based)
# ===============================

def extract_name(text):
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if len(line.split()) <= 3:
            if "email" not in line.lower():
                return line

    return "Not Found"


def match_score(resume, jd):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([resume, jd])

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

    similarity_part = (similarity / 100) * 40

    jd_skills = [
        "python", "react", "sql",
        "html", "css", "git",
        "aws", "node"
    ]

    found = 0

    for skill in jd_skills:
        if skill.lower() in resume.lower():
            found += 1

    skills_percent = (found / len(jd_skills)) * 100
    skills_part = (skills_percent / 100) * 40

    bonus = 0

    if len(resume) > 800:
        bonus += 10

    if re.search(r'\b(project|experience|education)\b', resume.lower()):
        bonus += 10

    # -----------------------
    # Final Score
    # -----------------------
    final_score = similarity_part + skills_part + bonus

    if final_score > 100:
        final_score = 100

    return round(final_score, 2)


def missing_skills(resume_skills, jd_skills):
    missing = []

    for skill in jd_skills:
        if skill.lower() not in [s.lower() for s in resume_skills]:
            missing.append(skill)

    return missing

def resume_tips(missing):
    tips = []

    if missing:
        tips.append("Add missing skills in projects or skills section.")

    if "sql" in missing:
        tips.append("Learn SQL basics and add to resume.")

    if "aws" in missing:
        tips.append("Add cloud basics / AWS certification.")

    if "git" in missing:
        tips.append("Mention Git / GitHub usage.")

    if "react" in missing:
        tips.append("Frontend projects with React can help.")

    if not tips:
        tips.append("Great resume! Keep projects updated.")

    return tips

def section_scores(skills, text):

    scores = {}

    # Skills
    scores["Skills"] = min(len(skills) * 10, 100)

    # Experience
    if "experience" in text.lower() or "internship" in text.lower():
        scores["Experience"] = 80
    else:
        scores["Experience"] = 40

    # Education
    if "b.tech" in text.lower() or "bca" in text.lower() or "mca" in text.lower():
        scores["Education"] = 85
    else:
        scores["Education"] = 50

    # Projects
    if "project" in text.lower():
        scores["Projects"] = 90
    else:
        scores["Projects"] = 45

    # Formatting
    if len(text) > 700:
        scores["Formatting"] = 75
    else:
        scores["Formatting"] = 55

    return scores

def ai_summary(name, skills, score, missing):

    summary = f"{name} has "

    if len(skills) >= 5:
        summary += "a strong technical skill set"
    elif len(skills) >= 3:
        summary += "a decent technical foundation"
    else:
        summary += "an improving technical profile"

    summary += f" with ATS score of {score}%. "

    if missing:
        summary += "Adding " + ", ".join(missing) + " can improve hiring chances. "

    if "python" in [s.lower() for s in skills]:
        summary += "Suitable for Python based roles."
    elif "react" in [s.lower() for s in skills]:
        summary += "Suitable for frontend roles."
    else:
        summary += "Suitable for entry-level software roles."

    return summary

def suggest_role(skills):
    skills = [s.lower() for s in skills]

    if "react" in skills and "javascript" in skills:
        return "Frontend Developer"

    elif "python" in skills and "sql" in skills:
        return "Python Developer"

    elif "python" in skills and "pandas" in skills:
        return "Data Analyst"

    return "Software Developer"


def resume_score(skills, education, experience):
    score = 0

    # Skills Score
    score += len(skills) * 5

    # Education Score
    if education != "Not Found":
        score += 20

    # Experience Score
    if experience == "Fresher":
        score += 10
    else:
        score += 20

    # Max limit
    if score > 100:
        score = 100

    return score

def ats_score(skills, education, experience, text):

    score = 0

    # Skills Score
    if len(skills) >= 6:
        score += 40
    elif len(skills) >= 4:
        score += 30
    elif len(skills) >= 2:
        score += 20

    # Education Score
    if education != "Not Found":
        score += 20

    # Experience Score
    if experience == "Fresher":
        score += 10
    elif "Years" in experience:
        score += 20

    # Keywords Score
    keywords = ["project", "internship", "developer", "python"]
    
    for word in keywords:
        if word in text.lower():
            score += 5

    if score > 100:
        score = 100

    return score

def better_suggestions(skills, education, experience, missing):

    tips = []

    if len(skills) < 5:
        tips.append("Add more technical skills.")

    if education == "Not Found":
        tips.append("Add education details clearly.")

    if experience == "Not Found":
        tips.append("Mention internships or experience.")

    if "sql" in missing:
        tips.append("Learn SQL and add projects.")

    if "aws" in missing:
        tips.append("Learn cloud basics / AWS.")

    if not tips:
        tips.append("Resume looks strong. Keep improving projects.")

    return tips


def role_recommendation(skills):

    if "react" in skills or "html" in skills:
        return "Frontend Developer"

    elif "python" in skills and "sql" in skills:
        return "Python Developer"

    elif "aws" in skills:
        return "Cloud Engineer"

    else:
        return "Software Developer"

# ===============================
# 📄 File Path
# ===============================
file_path = "uploads/resume.pdf"


# ===============================
# 📄 Extract Resume Text
# ===============================
text = extract_text(file_path)

job_description = """
Looking for Python Developer with React, SQL, Git,
HTML, CSS knowledge. Fresher can apply.
"""
jd_skills = ["python", "react", "sql", "git", "html", "css", "aws"]

experience = extract_experience(text)
education = extract_education(text)
name = extract_name(text)
skills = extract_skills(text)

score = ats_score(skills, education, experience, text)

final_score = resume_score(skills, education, experience)
missing = missing_skills(skills, jd_skills)
tips = better_suggestions(skills, education, experience, missing)
role = role_recommendation(skills)

print("\n===== NLP DATA =====\n")
print("Name:", name)
print("Skills:", skills)

# ===============================
# 📧 Email Extract
# ===============================
email = re.findall(r'\S+@\S+', text)


# ===============================
# 📱 Phone Extract
# ===============================
phone = re.findall(r'\+91[-\s]?\d{10}', text)


# ===============================
# 🔗 LinkedIn Extract
# ===============================
linkedin = re.findall(r'linkedin\.com/\S+', text)


# ===============================
# 🔗 GitHub Extract
# ===============================
github = re.findall(r'github\.com/\S+', text)


# ===============================
# 🎯 Final Output
# ===============================
print("\n===== EXTRACTED DATA =====\n")

print("Name:", name)
print("Email:", email[0] if email else "")
print("Phone:", phone[0] if phone else "")
print("LinkedIn:", linkedin[0] if linkedin else "")
print("GitHub:", github[0] if github else "")
print("Skills:", skills)
print("Experience:", experience)
print("Education:", education)
print("Match Score:", score, "%")
print("Missing Skills:", missing)
print("Resume Tips:", tips)
print("Best Job Role:", role)
print("Resume Score:", final_score, "/100")