import pdfplumber
import pytesseract
import re

from pdf2image import convert_from_path

# Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ----------------------------
# Extract Text from PDF
# ----------------------------
def extract_text(file_path):

    text = ""

    # Normal PDF Read
    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except:
        text = ""

    # OCR Fallback if no text found
    if text.strip() == "":

        try:
            images = convert_from_path(file_path)

            for img in images:
                text += pytesseract.image_to_string(img)

        except:
            text = "Unable to read PDF"

    return text


# ----------------------------
# Clean Text
# ----------------------------
def clean_text(text):

    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()