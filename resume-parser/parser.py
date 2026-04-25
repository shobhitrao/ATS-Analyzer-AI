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
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = extract_pdf_text(file_path)

    elif ext == ".docx":
        text = extract_docx_text(file_path)

    else:
        text = ""

    return clean_text(text)


# ==========================
# PDF TEXT EXTRACTION
# ==========================
def extract_pdf_text(file_path):
    text = ""

    # 1. pdfplumber (best layout)
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

    except:
        pass

    # 2. PyPDF2 fallback
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        if text.strip():
            return text

    except:
        pass

    # 3. OCR fallback
    try:
        images = convert_from_path(file_path)

        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

        if text.strip():
            return text

    except:
        pass

    return "Unable to read PDF"


# ==========================
# DOCX TEXT
# ==========================
def extract_docx_text(file_path):
    text = ""

    try:
        doc = Document(file_path)

        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"

    except:
        pass

    return text


# ==========================
# CLEAN TEXT
# ==========================
def clean_text(text):
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned.append(line)

    return "\n".join(cleaned)
