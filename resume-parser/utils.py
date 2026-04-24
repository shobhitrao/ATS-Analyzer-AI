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
        "python", "java", "html", "css", "javascript",
        "sql", "flask", "django", "react", "nodejs"
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
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())

    if len(jd_words) == 0:
        return 0

    matched = resume_words.intersection(jd_words)
    return int((len(matched) / len(jd_words)) * 100)


def detect_experience(text):
    text = text.lower()

    if "year" in text or "years" in text:
        return "Experienced"

    if "intern" in text or "fresher" in text:
        return "Fresher"

    return "Not Found"


def missing_skills(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    missing = []

    for skill in jd_skills:
        if skill not in resume_skills:
            missing.append(skill)

    return missing


def resume_tips(text):
    return [
        "Add more technical skills",
        "Improve formatting",
        "Add projects section",
        "Use action words"
    ]


def ai_summary(text):
    return "Good resume with decent skills and structure."


def section_scores(text):
    return {
        "Skills": 80,
        "Experience": 70,
        "Projects": 75,
        "Education": 85
    }