import re


# ==========================
# NAME
# ==========================
def extract_name(text):
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if 2 < len(line) < 40:
            if len(line.split()) <= 4:
                if "@" not in line:
                    return line

    return "Name Not Found"


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
        "python", "java", "html", "css", "javascript",
        "sql", "flask", "django", "react", "nodejs",
        "aws", "git", "github", "mongodb", "mysql",
        "pandas", "numpy"
    ]

    found = []
    lower = text.lower()

    for skill in skills:
        if skill in lower:
            found.append(skill)

    return list(set(found))


def advanced_skills(text):
    return extract_skills(text)


# ==========================
# ATS SCORE
# ==========================

def match_score(resume_text, jd_text):
    text = resume_text.lower()
    jd = jd_text.lower()

    score = 0

    # 1. Skills Score
    skills = extract_skills(resume_text)

    if len(skills) >= 8:
        score += 30
    elif len(skills) >= 5:
        score += 22
    elif len(skills) >= 3:
        score += 15
    else:
        score += 8

    # 2. Experience
    if "year" in text or "years" in text:
        score += 20
    elif "intern" in text:
        score += 12
    else:
        score += 5

    # 3. Projects
    if "project" in text:
        score += 15

    # 4. Education
    if "btech" in text or "b.tech" in text or "mca" in text or "bca" in text:
        score += 15

    # 5. JD Match
    jd_words = set(jd.split())
    resume_words = set(text.split())

    if jd_words:
        matched = len(jd_words & resume_words)
        score += int((matched / len(jd_words)) * 15)

    # 6. Resume Length
    if len(resume_text) > 500:
        score += 5

    # Final Limit
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
    resume = extract_skills(resume_text)
    jd = extract_skills(jd_text)

    return [skill for skill in jd if skill not in resume]


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

    skills_found = len(extract_skills(text))

    if skills_found >= 8:
        skills_score = 95
    elif skills_found >= 6:
        skills_score = 85
    elif skills_found >= 4:
        skills_score = 70
    elif skills_found >= 2:
        skills_score = 55
    else:
        skills_score = 35

    if "5 years" in t or "4 years" in t or "3 years" in t:
        exp_score = 95
    elif "2 years" in t or "1 year" in t:
        exp_score = 80
    elif "intern" in t:
        exp_score = 65
    elif "fresher" in t:
        exp_score = 55
    else:
        exp_score = 40

    if "project" in t and "github" in t:
        project_score = 95
    elif "project" in t:
        project_score = 80
    else:
        project_score = 35

    if "m.tech" in t or "mba" in t or "mca" in t:
        edu_score = 92
    elif "b.tech" in t or "btech" in t or "bca" in t:
        edu_score = 82
    else:
        edu_score = 35

    return {
        "Skills": skills_score,
        "Experience": exp_score,
        "Projects": project_score,
        "Education": edu_score
    }