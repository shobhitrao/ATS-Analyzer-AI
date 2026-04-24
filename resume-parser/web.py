import re

def extract_name(text):
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) > 2 and len(line.split()) <= 4:
            return line
    return "Name Not Found"


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not Found"


def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,15}', text)
    return match.group(0) if match else "Not Found"


def extract_skills(text):
    skills = [
        "python","java","html","css","javascript",
        "sql","flask","django","react","nodejs","aws","git"
    ]
    found = []
    lower = text.lower()

    for skill in skills:
        if skill in lower:
            found.append(skill)

    return found


def advanced_skills(text):
    return extract_skills(text)


def match_score(resume_text, jd_text):
    rw = set(resume_text.lower().split())
    jw = set(jd_text.lower().split())

    if not jw:
        return 0

    return int(len(rw & jw) / len(jw) * 100)


def detect_experience(text):
    t = text.lower()

    if "years" in t or "year" in t:
        return "Experienced"

    if "intern" in t or "fresher" in t:
        return "Fresher"

    return "Not Found"


def missing_skills(skills, jd_skills):
    return [x for x in jd_skills if x not in skills]


def resume_tips(missing):
    if missing:
        return [f"Add {x}" for x in missing]
    return ["Resume looks good"]


def ai_summary(name, skills, score, missing):
    return f"{name} has {len(skills)} skills with ATS score {score}%."


def section_scores(skills, text):
    return {
        "Skills": min(len(skills) * 10, 100),
        "Experience": 70,
        "Projects": 75,
        "Education": 80
    }