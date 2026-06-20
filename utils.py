import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================
# NAME
# ==========================

def extract_name(text):

    lines = [x.strip() for x in text.split("\n") if x.strip()]

    bad = [
        "email", "phone", "linkedin", "github",
        "career", "objective", "education",
        "skills", "project", "experience"
    ]

    for line in lines[:12]:

        low = line.lower()

        if any(b in low for b in bad):
            continue

        if "@" in line or "http" in low:
            continue

        if re.match(r'^[A-Za-z ]+$', line):

            words = line.split()

            if 2 <= len(words) <= 3:
                return " ".join(w.capitalize() for w in words)

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
# MASTER SKILLS
# ==========================

MASTER_SKILLS = [

    "python",
    "java",
    "c",
    "c++",
    "html",
    "css",
    "javascript",
    "react",
    "nodejs",
    "sql",
    "mysql",
    "mongodb",
    "flask",
    "django",
    "fastapi",
    "git",
    "github",
    "aws",
    "docker",
    "machine learning",
    "deep learning",
    "data analysis",
    "pandas",
    "numpy",
    "api"
]


# ==========================
# SKILLS
# ==========================

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in MASTER_SKILLS:

        pattern = r'\b' + re.escape(skill) + r'\b'

        if re.search(pattern, text):
            found.append(skill.title())

    return list(set(found))


# ==========================
# ATS SCORE
# ==========================

def match_score(resume_text, jd_text):

    resume = resume_text.lower()
    jd = jd_text.lower()

    # Cosine Similarity
    documents = [resume, jd]

    cv = CountVectorizer()

    matrix = cv.fit_transform(documents)

    similarity = cosine_similarity(matrix)[0][1]

    score = int(similarity * 100)

    # Bonus logic
    if "project" in resume:
        score += 5

    if "experience" in resume:
        score += 10

    if "github" in resume:
        score += 5

    # limit
    if score > 95:
        score = 95

    # minimum realistic score
    if score < 40:
        score += 25

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

def missing_skills(skills, jd_skills):

    resume_skills = [x.lower().strip() for x in skills]

    jd_required = [x.lower().strip() for x in jd_skills]

    missing = []

    for skill in jd_required:

        if skill not in resume_skills:
            missing.append(skill.title())

    return missing


# ==========================
# RESUME TIPS
# ==========================

def resume_tips(missing):

    tips = []

    if missing:

        for skill in missing:
            tips.append(f"Add {skill} skill in resume")

    else:
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


# ==========================
# ADVANCED SKILLS
# ==========================

def advanced_skills(text):

    return extract_skills(text)