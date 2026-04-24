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
        "sql", "flask", "django", "react", "nodejs",
        "c++", "bootstrap", "mongodb", "mysql",
        "power bi", "excel"
    ]

    found = []
    lower = text.lower()

    for skill in skills:
        if skill in lower:
            found.append(skill)

    return found


def advanced_skills(text):
    return extract_skills(text)