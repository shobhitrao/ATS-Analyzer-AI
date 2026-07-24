import os
import re
import pdfplumber
import pytesseract
import PyPDF2
from pdf2image import convert_from_path
from docx import Document


# Windows only path
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ==========================
# MAIN EXTRACT TEXT
# ==========================
def extract_text(file_path):

    if not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            text = extract_pdf_text(file_path)

        elif ext == ".docx":
            text = extract_docx_text(file_path)

        else:
            return ""

        return clean_text(text)

    except Exception as e:
        print(f"Extract Error: {e}")
        return ""

# ==========================
# PDF TEXT EXTRACTION
# ==========================
def extract_pdf_text(file_path):
    text = ""

    # 1. pdfplumber (Best Quality)
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=2
                )

                if page_text:
                    text += page_text + "\n"

        if text.strip():
            return text

    except Exception as e:
        print(f"pdfplumber Error: {e}")

    # 2. PyPDF2 Fallback
    try:
        text = ""

        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        if text.strip():
            return text

    except Exception as e:
        print(f"PyPDF2 Error: {e}")

    # 3. OCR Fallback
    try:
        text = ""

        images = convert_from_path(
            file_path,
            dpi=300,
            fmt="jpeg"
        )

        for img in images:
            page = pytesseract.image_to_string(
                img,
                lang="eng",
                config="--oem 3 --psm 6"
            )

            if page.strip():
                text += page + "\n"

        if text.strip():
            return text

    except Exception as e:
        print(f"OCR Error: {e}")

    return ""


# ==========================
# DOCX TEXT EXTRACTION
# ==========================
def extract_docx_text(file_path):
    text = ""

    try:
        doc = Document(file_path)

        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"

    except Exception as e:
        print(f"DOCX Error: {e}")

    return text


# ==========================
# CLEAN TEXT
# ==========================
def clean_text(text):

    if not text:
        return ""

    lines = []
    seen = set()

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(r"[ \t]+", " ", line)

        if line not in seen:
            seen.add(line)
            lines.append(line)

    text = "\n".join(lines)

    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()