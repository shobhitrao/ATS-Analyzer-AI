import pdfplumber
import pytesseract
import re
import os
from pdf2image import convert_from_path


# Windows only path (optional)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ==========================
# EXTRACT TEXT FROM PDF
# ==========================
def extract_text(file_path):
    text = ""

    # Normal text PDF
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        text = ""

    # OCR fallback
    if not text.strip():
        try:
            images = convert_from_path(file_path)

            for img in images:
                text += pytesseract.image_to_string(img)
        except:
            text = "Unable to read PDF"

    return clean_text(text)


# ==========================
# CLEAN TEXT
# ==========================
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()