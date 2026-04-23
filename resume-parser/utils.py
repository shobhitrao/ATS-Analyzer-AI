import re


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,15}', text)
    return match.group(0) if match else "Not Found"

def extract_name(text):
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) > 2 and len(line.split()) <= 3:
            return line
    return "Unknown"

def detect_experience(text):
    text = text.lower()

    patterns = [
        r'(\d+)\+?\s+years',
        r'(\d+)\+?\s+yrs',
        r'(\d+)\+?\s+year',
        r'(\d+)\+?\s+yr'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1) + " Years"

    if "internship" in text:
        return "Internship Experience"

    if "fresher" in text:
        return "Fresher"

    return "Not Mentioned"


# Extract Email
def extract_email(text):
    match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match[0] if match else None

# Extract Name (basic)
def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

# Extract Skills (simple keyword match)
skills_list = [
    "python", "java", "c++", "html", "css", "javascript",
    "react", "node", "sql", "mongodb", "machine learning"
]

def extract_skills(text):
    skills_list = [
        "python","java","c++","html","css","javascript","sql",
        "flask","django","react","node","machine learning",
        "excel","power bi"
    ]
    found = []
    lower_text = text.lower()

    for skill in skills_list:
        if skill in lower_text:
            found.append(skill)

    return found

def advanced_skills(text):
    return extract_skills(text)

def detect_experience(text):

    text = text.lower()

    # Fresher detect
    if "fresher" in text:
        return "Fresher"

    if "internship" in text:
        return "Internship Experience"

    # Years detect
    match = re.search(r'(\d+)\+?\s*(year|years)', text)

    if match:
        return match.group(1) + " Years Experience"

    # Months detect
    match2 = re.search(r'(\d+)\s*(month|months)', text)

    if match2:
        return match2.group(1) + " Months Experience"

    return "Not Mentioned"

import re

def detect_experience(text):

    text = text.lower()

    if "fresher" in text:
        return "Fresher"

    match = re.search(r'(\d+)\s*(year|years)', text)

    if match:
        return match.group(1) + " Years Experience"

    return "Not Mentioned"


def advanced_skills(text):

    skills_db = [
        "python", "html", "css", "javascript",
        "react", "git", "github", "sql",
        "aws", "pandas", "flask"
    ]

    found = []

    text = text.lower()

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return found

def match_score(resume_text, jd_text):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    resume_skills = set(advanced_skills(resume_text))
    jd_skills = set(advanced_skills(jd_text))

    if len(jd_skills) == 0:
        return 30

    matched = len(resume_skills.intersection(jd_skills))

    skill_score = (matched / len(jd_skills)) * 70

    bonus = 0

    if "project" in resume_text:
        bonus += 10

    if "experience" in resume_text:
        bonus += 10

    if "education" in resume_text:
        bonus += 10

    score = int(skill_score + bonus)

    if score >= 100:
        score = 95

    if score < 20:
        score = 20

    return score

    # Bonus checks
    bonus = 0

    if "project" in resume_text.lower():
        bonus += 10

    if "experience" in resume_text.lower():
        bonus += 10

    if "education" in resume_text.lower():
        bonus += 10

    score = int(skill_score + bonus)

    if score > 95:
        score = 95   # direct 100 avoid

    return score
def missing_skills(user_skills, jd_skills):
    return [skill for skill in jd_skills if skill not in user_skills]

def resume_tips(missing):
    tips = []
    for skill in missing:
        tips.append(f"Add {skill} in projects or skills section.")
    return tips

# ===============================
# AI SUMMARY FUNCTION
# ===============================
def ai_summary(name, skills, score, missing):

    top_skills = ", ".join(skills[:5])

    if score >= 85:
        level = "excellent"
    elif score >= 70:
        level = "strong"
    elif score >= 50:
        level = "average"
    else:
        level = "needs improvement"

    if missing:
        miss = ", ".join(missing[:3])
        improve = f" Adding {miss} can improve hiring chances."
    else:
        improve = " No major skills missing."

    return f"{name} has a {level} resume with ATS score of {score}%. Strong skills include {top_skills}.{improve}"

# ===============================
# SECTION SCORES FUNCTION
# ===============================
def section_scores(skills, text):

    text = text.lower()

    scores = {
        "Skills": 90 if len(skills) >= 5 else 70,
        "Experience": 85 if "experience" in text else 60,
        "Education": 85 if "education" in text or "b.tech" in text or "bca" in text else 65,
        "Projects": 90 if "project" in text else 60,
        "Formatting": 80
    }

    return scores