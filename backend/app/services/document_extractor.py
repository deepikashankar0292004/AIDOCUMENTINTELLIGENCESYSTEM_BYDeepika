import fitz
import pytesseract

from PIL import Image
from io import BytesIO
from pypdf import PdfReader


# Tell Python where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF.

    First tries normal PDF text extraction.
    If no text is found, uses OCR with Tesseract.
    """

    # -----------------------------------
    # Step 1: Try normal PDF text extraction
    # -----------------------------------

    reader = PdfReader(file_path)

    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text + "\n"

    extracted_text = extracted_text.strip()

    # If text was found, return it
    if extracted_text:
        return extracted_text

    # -----------------------------------
    # Step 2: Use OCR for scanned PDF
    # -----------------------------------

    print("No text found. Starting OCR...")

    ocr_text = ""

    # Open PDF using PyMuPDF
    pdf_document = fitz.open(file_path)

    for page_number in range(len(pdf_document)):

        print(f"OCR processing page {page_number + 1}...")

        page = pdf_document[page_number]

        # Render PDF page as an image
        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        # Convert image bytes to PIL Image
        image = Image.open(
            BytesIO(pix.tobytes("png"))
        )

        # Run Tesseract OCR
        text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        ocr_text += text + "\n"

    pdf_document.close()

    return ocr_text.strip()


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.
    """

    print("Starting OCR for image...")

    image = Image.open(file_path)

    extracted_text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return extracted_text.strip()