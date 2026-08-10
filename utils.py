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

    # Supports common Indian formats such as:
    # +91 98765 43210, +91-9876543210, 98765 43210, 9876543210
    phone_patterns = [
        r'\+91[\s-]*\d{5}[\s-]*\d{5}',
        r'\b[6-9]\d{4}[\s-]\d{5}\b',
        r'\b[6-9]\d{9}\b',
    ]

    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()

    return "Not Found"


# ==========================
# MASTER SKILLS
# ==========================

MASTER_SKILLS = [

    # Programming
    "python","java","c","c++","c#","go","rust","kotlin","swift","php","ruby",

    # Web
    "html","css","javascript","typescript","bootstrap","tailwind css",

    # Frontend
    "react","next.js","angular","vue","redux",

    # Backend
    "nodejs","express","django","flask","fastapi","spring boot","laravel",

    # Database
    "sql","mysql","postgresql","sqlite","mongodb","redis","oracle",

    # Cloud
    "aws","azure","google cloud","gcp",

    # DevOps
    "docker","kubernetes","jenkins","github actions","ci/cd","linux","nginx",

    # Data Science
    "numpy","pandas","matplotlib","seaborn","scikit-learn",
    "tensorflow","keras","pytorch","opencv",

    # AI
    "machine learning","deep learning","nlp",
    "generative ai","llm","langchain","huggingface",

    # APIs
    "rest api","graphql","api",

    # Version Control
    "git","github","gitlab","bitbucket",

    # Mobile
    "android","flutter","react native",

    # Office
    "excel","power bi","tableau",

    # Misc
    "firebase","supabase","figma","jira","postman"
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
    """
    JD match score out of 100:
    - 70 points: required technical skills matched
    - 20 points: text similarity
    - 10 points: resume quality signals
    """
    resume_skills = {s.lower() for s in advanced_skills(resume_text)}
    jd_skills = {s.lower() for s in advanced_skills(jd_text)}

    resume = resume_text.lower()
    jd = jd_text.lower()

    if jd_skills:
        matched = len(resume_skills & jd_skills)
        skill_score = (matched / len(jd_skills)) * 70
    else:
        # If the JD has no recognizable technical skills, don't unfairly
        # penalize the candidate.
        skill_score = 35

    try:
        cv = CountVectorizer(stop_words="english")
        matrix = cv.fit_transform([resume, jd])
        similarity = float(cosine_similarity(matrix)[0][1])
        similarity_score = similarity * 20
    except (ValueError, IndexError):
        similarity_score = 0

    quality = 0
    if re.search(r'\b(project|projects)\b', resume):
        quality += 3
    if re.search(r'\b(experience|internship|intern)\b', resume):
        quality += 3
    if re.search(r'\blinkedin\b', resume):
        quality += 2
    if re.search(r'\bgithub\b', resume):
        quality += 2

    return max(0, min(100, round(skill_score + similarity_score + quality)))


# ==========================
# EXPERIENCE
# ==========================

def detect_experience(text):

    t = text.lower()

    # Internship
    if re.search(r"\bintern(ship)?\b", t):
        return "Internship Experience"

    # Fresher
    if re.search(r"\bfresher\b", t):
        return "Fresher"

    # Match: 1 year, 2 years, 3 yrs, 5+ years
    match = re.search(r'(\d+)\s*(\+)?\s*(year|years|yr|yrs)', t)

    if match:
        years = int(match.group(1))

        if years >= 8:
            return "8+ Years Experience"

        elif years >= 5:
            return "5+ Years Experience"

        elif years >= 3:
            return "3+ Years Experience"

        elif years >= 1:
            return "1+ Year Experience"

    # Match date ranges like 2022-2025
    date_match = re.findall(r'(20\d{2})', t)

    if len(date_match) >= 2:
        start = int(date_match[0])
        end = int(date_match[-1])

        if end > start:
            return f"{end-start} Years Experience"

    return "Experience Not Found"


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
    """Return transparent, resume-only section scores out of 100."""
    t = text.lower()

    # ---------------- Skills ----------------
    skill_count = len(advanced_skills(text))
    if skill_count >= 15:
        skills = 95
    elif skill_count >= 10:
        skills = 85
    elif skill_count >= 7:
        skills = 75
    elif skill_count >= 4:
        skills = 65
    elif skill_count >= 1:
        skills = 55
    else:
        skills = 30

    # ---------------- Experience ----------------
    exp = 50
    if re.search(r'8\s*\+?\s*(year|years|yr|yrs)', t):
        exp = 95
    elif re.search(r'5\s*\+?\s*(year|years|yr|yrs)', t):
        exp = 90
    elif re.search(r'3\s*\+?\s*(year|years|yr|yrs)', t):
        exp = 80
    elif re.search(r'[12]\s*\+?\s*(year|years|yr|yrs)', t):
        exp = 70
    elif re.search(r'\bintern(ship)?\b', t):
        exp = 60
    elif re.search(r'\bfresher\b', t):
        exp = 55
    else:
        # A resume can still be valid without explicitly stating years.
        # Give a neutral score rather than assuming zero experience.
        exp = 50

    # ---------------- Projects ----------------
    project_signals = [
        r'\bprojects?\b',
        r'\bgithub\b',
        r'\bportfolio\b',
        r'\bapi\b',
        r'\bmachine learning\b',
        r'\bweb application\b'
    ]
    project_count = sum(bool(re.search(pattern, t)) for pattern in project_signals)

    if project_count >= 5:
        proj = 95
    elif project_count >= 3:
        proj = 85
    elif project_count >= 2:
        proj = 75
    elif project_count >= 1:
        proj = 65
    else:
        proj = 40

    # ---------------- Education ----------------
    if re.search(r'\b(phd|doctorate)\b', t):
        edu = 95
    elif re.search(r'\b(m\.tech|mtech|mba|mca|master(?:s)?|post\s*graduate)\b', t):
        edu = 90
    elif re.search(r'\b(b\.tech|btech|b\.e|b\.eng|be|bca|b\.sc|bsc|bcom|b\.com|bachelor)\b', t):
        edu = 80
    elif re.search(r'\bdiploma\b', t):
        edu = 70
    elif re.search(r'\b(12th|intermediate|higher secondary)\b', t):
        edu = 60
    else:
        edu = 40

    # ---------------- Format ----------------
    # Check real extracted contact information rather than the strings
    # "Not Found" / "Candidate", which are truthy in Python.
    name_found = extract_name(text) != "Candidate"
    email_found = extract_email(text) != "Not Found"
    phone_found = extract_phone(text) != "Not Found"

    format_score = 0
    format_score += 20 if name_found else 0
    format_score += 20 if email_found else 0
    format_score += 20 if phone_found else 0
    format_score += 20 if len(text.strip()) > 500 else 10 if len(text.strip()) > 250 else 0
    format_score += 20 if re.search(
        r'\b(education|skills|experience|projects?|certifications?|summary|objective)\b',
        t
    ) else 0

    # ---------------- Contact ----------------
    contact = 0
    contact += 30 if name_found else 0
    contact += 35 if email_found else 0
    contact += 35 if phone_found else 0

    return {
        "Skills": skills,
        "Experience": exp,
        "Projects": proj,
        "Education": edu,
        "Format": format_score,
        "Contact": contact,
    }


# ==========================
# ADVANCED SKILLS
# ==========================

def advanced_skills(text):

    text = text.lower()

    aliases = {
        "nodejs": ["node.js", "node js", "nodejs"],
        "next.js": ["next.js", "next js", "nextjs"],
        "react": ["react", "react.js", "reactjs"],
        "javascript": ["javascript", "js"],
        "typescript": ["typescript", "ts"],
        "c++": ["c++", "cpp"],
        "c#": ["c#", "c sharp"],
        "postgresql": ["postgresql", "postgres"],
        "google cloud": ["google cloud", "gcp"],
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning", "dl"],
        "artificial intelligence": ["artificial intelligence", "ai"],
        "power bi": ["power bi", "powerbi"],
        "github": ["github", "git hub"]
    }

    found = set()

    # Check aliases
    for skill, names in aliases.items():
        for name in names:
            if re.search(r"\b" + re.escape(name) + r"\b", text):
                found.add(skill.title())
                break

    # Check remaining master skills
    for skill in MASTER_SKILLS:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text):
            found.add(skill.title())

    return sorted(found)