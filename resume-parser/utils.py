import re


# ==========================
# NAME
# ==========================


import re

def extract_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    blocked_words = {
        "email", "phone", "linkedin", "github", "address",
        "summary", "profile", "skills", "experience",
        "education", "projects", "certifications",
        "objective", "resume", "cv"
    }

    # top lines me search
    for line in lines[:15]:
        low = line.lower()

        # skip unwanted lines
        if any(word in low for word in blocked_words):
            continue

        if "@" in line:
            continue

        if re.search(r'\d', line):
            continue

        # remove symbols
        clean = re.sub(r'[^A-Za-z ]', '', line).strip()
        words = clean.split()

        # 2 to 4 words likely person name
        if 2 <= len(words) <= 4:
            good = True
            for w in words:
                if len(w) < 2:
                    good = False

            if good:
                return " ".join(x.capitalize() for x in words)

    # fallback from email
    email = re.search(r'([\w\.-]+)@', text)
    if email:
        username = email.group(1)
        username = username.replace(".", " ").replace("_", " ")
        words = username.split()

        if 1 <= len(words) <= 3:
            return " ".join(x.capitalize() for x in words)

    return "Candidate"

# ==========================
# EMAIL
# ==========================
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not Found"


# ==========================
# PHONE
# ==========================
def extract_phone(text):
    match = re.search(r'(\+91[-\s]?\d{10}|\d{10})', text)
    return match.group(0) if match else "Not Found"


# ==========================
# SKILLS
# ==========================
def extract_skills(text):
    skills = [
        "python","java","html","css","javascript",
        "sql","flask","django","react","nodejs",
        "aws","git","github","mongodb","mysql",
        "numpy","pandas","excel","power bi",
        "machine learning","data analysis",
        "c++","c","php","bootstrap"
    ]

    found = []
    lower = text.lower()

    for skill in skills:
        if skill in lower:
            found.append(skill.title())

    return list(set(found))


# ==========================
# ATS SCORE
# ==========================

def match_score(resume_text, jd_text):
    sections = section_scores(resume_text)

    avg = (
        sections["Skills"] +
        sections["Experience"] +
        sections["Projects"] +
        sections["Education"]
    ) / 4

    # JD Match Bonus
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)

    matched = 0

    for skill in jd_skills:
        if skill in resume_skills:
            matched += 1

    if jd_skills:
        bonus = int((matched / len(jd_skills)) * 15)
    else:
        bonus = 8

    score = int(avg + bonus)

    if score > 100:
        score = 100

    return score



# ==========================
# EXPERIENCE
# ==========================
def detect_experience(text):
    t = text.lower()

    if "year" in t or "years" in t:
        return "Experienced"

    if "intern" in t or "fresher" in t:
        return "Fresher"

    return "Not Found"


# ==========================
# MISSING SKILLS
# ==========================

def missing_skills(resume_text, jd_text):
    resume_skills = [x.lower() for x in extract_skills(resume_text)]
    jd_skills = [x.lower() for x in extract_skills(jd_text)]

    missing = []

    for skill in jd_skills:
        if skill not in resume_skills:
            missing.append(skill.title())

    return missing


# ==========================
# TIPS
# ==========================
def resume_tips(missing):
    tips = []

    if missing:
        for skill in missing:
            tips.append(f"Add {skill} skill in resume")

    if not tips:
        tips.append("Resume looks strong")

    return tips


# ==========================
# AI SUMMARY
# ==========================
def ai_summary(name, skills, score, missing):
    msg = f"{name} has {len(skills)} technical skills with ATS score {score}%. "

    if missing:
        msg += "Adding missing skills can improve hiring chances."

    else:
        msg += "Profile looks strong for job applications."

    return msg


# ==========================
# SECTION SCORES
# ==========================

def section_scores(text):
    t = text.lower()

    # Skills
    skill_count = len(extract_skills(text))

    if skill_count >= 8:
        skills = 90
    elif skill_count >= 6:
        skills = 80
    elif skill_count >= 4:
        skills = 70
    else:
        skills = 55

    # Experience
    if "5 years" in t or "4 years" in t or "3 years" in t:
        exp = 88
    elif "2 years" in t or "1 year" in t:
        exp = 78
    elif "intern" in t:
        exp = 68
    elif "fresher" in t:
        exp = 60
    else:
        exp = 55

    # Projects
    if "project" in t and "github" in t:
        proj = 90
    elif "project" in t:
        proj = 78
    elif "portfolio" in t:
        proj = 70
    else:
        proj = 58

    # Education
    if "m.tech" in t or "mba" in t or "mca" in t:
        edu = 88
    elif "b.tech" in t or "btech" in t or "bca" in t or "b.sc" in t:
        edu = 80
    elif "12th" in t:
        edu = 65
    else:
        edu = 55

    return {
        "Skills": skills,
        "Experience": exp,
        "Projects": proj,
        "Education": edu
    }