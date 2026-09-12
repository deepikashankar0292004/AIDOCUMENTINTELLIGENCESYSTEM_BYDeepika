from io import BytesIO
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_PAGES = 3


def validate_document(
    filename: str,
    file_content: bytes
) -> dict:

    # Check whether the file is empty
    if not file_content:
        return {
            "valid": False,
            "error": "The uploaded file is empty."
        }

    # Check file extension
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": (
                "Unsupported file format. "
                "Only PDF, JPG, JPEG and PNG files are allowed."
            )
        }

    # Validate PDF
    if extension == ".pdf":

        try:
            pdf_stream = BytesIO(file_content)
            reader = PdfReader(pdf_stream)

            page_count = len(reader.pages)

        except Exception:
            return {
                "valid": False,
                "error": "The PDF file is corrupted or cannot be read."
            }

        if page_count == 0:
            return {
                "valid": False,
                "error": "The PDF does not contain any pages."
            }

        if page_count > MAX_PAGES:
            return {
                "valid": False,
                "error": (
                    f"The document contains {page_count} pages. "
                    f"The maximum allowed is {MAX_PAGES} pages."
                )
            }

        return {
            "valid": True,
            "file_type": "pdf",
            "page_count": page_count
        }

    # Validate JPG / PNG
    try:
        image_stream = BytesIO(file_content)

        with Image.open(image_stream) as image:
            image.verify()

    except Exception:
        return {
            "valid": False,
            "error": "The image file is corrupted or cannot be read."
        }

    return {
        "valid": True,
        "file_type": extension.replace(".", ""),
        "page_count": 1
    }