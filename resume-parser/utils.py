import re




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
    text = text.lower()
    found = []
    for skill in skills_list:
        if skill in text:
            found.append(skill)
    return list(set(found))

def advanced_skills(text):

    skills_db = [
        "python", "java", "c++", "html", "css",
        "javascript", "react", "node", "flask",
        "django", "sql", "mysql", "mongodb",
        "git", "github", "aws", "docker"
    ]

    found = []

    text = text.lower()

    for skill in skills_db:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found.append(skill)

    return found

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
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    if not jd_skills:
        return 75

    matched = 0

    for skill in jd_skills:
        if skill in resume_skills:
            matched += 1

    score = int((matched / len(jd_skills)) * 100)
    return score

def missing_skills(user_skills, jd_skills):
    return [skill for skill in jd_skills if skill not in user_skills]

def resume_tips(missing):
    tips = []
    for skill in missing:
        tips.append(f"Add {skill} in projects or skills section.")
    return tips