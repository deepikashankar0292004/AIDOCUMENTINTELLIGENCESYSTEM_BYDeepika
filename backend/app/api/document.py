import uuid
import json
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.app.services.document_validator import validate_document
from backend.app.services.document_extractor import (
    extract_text_from_pdf,
    extract_text_from_image
)
from backend.app.services.ai_extractor import create_structured_result
from backend.app.services.data_validator import validate_structured_data

from backend.app.core.database import get_db
from backend.app.models.document import Document


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)


UPLOAD_DIRECTORY = Path("uploads")

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # -------------------------------------------------
    # 1. Read uploaded file
    # -------------------------------------------------

    file_content = await file.read()

    # -------------------------------------------------
    # 2. Validate document
    # -------------------------------------------------

    validation_result = validate_document(
        file.filename,
        file_content
    )

    if not validation_result["valid"]:

        return {
            "success": False,
            "filename": file.filename,
            "error": validation_result["error"]
        }

    # -------------------------------------------------
    # 3. Create unique filename
    # -------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = (
        UPLOAD_DIRECTORY / unique_filename
    )

    # -------------------------------------------------
    # 4. Save uploaded file
    # -------------------------------------------------

    with open(
        file_path,
        "wb"
    ) as output_file:

        output_file.write(
            file_content
        )

    # -------------------------------------------------
    # 5. Extract text
    # -------------------------------------------------

    extracted_text = ""

    if validation_result["file_type"] == "pdf":

        extracted_text = extract_text_from_pdf(
            str(file_path)
        )

    elif validation_result["file_type"] in [
        "jpg",
        "jpeg",
        "png"
    ]:

        extracted_text = extract_text_from_image(
            str(file_path)
        )

    # -------------------------------------------------
    # 6. AI structured extraction
    # -------------------------------------------------

    structured_result = create_structured_result(
        validation_result["file_type"],
        extracted_text
    )

    # -------------------------------------------------
    # 7. Validate AI result
    # -------------------------------------------------

    ai_validation_result = validate_structured_data(
        structured_result
    )

    # -------------------------------------------------
    # 8. Prepare database values
    # -------------------------------------------------

    document_type = structured_result.get(
        "document_type"
    )

    structured_data = structured_result.get(
        "data",
        {}
    )

    validation_status = ai_validation_result.get(
        "status"
    )

    processing_metadata = {
        "file_type": validation_result["file_type"],
        "page_count": validation_result["page_count"],
        "validation": ai_validation_result
    }

    # -------------------------------------------------
    # 9. Save document in database
    # -------------------------------------------------

    document = Document(
        document_name=file.filename,
        file_type=validation_result["file_type"],
        document_type=document_type,
        file_path=str(file_path),
        extracted_text=extracted_text,
        structured_data=json.dumps(
            structured_data
        ),
        validation_status=validation_status,
        processing_metadata=json.dumps(
            processing_metadata
        )
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    # -------------------------------------------------
    # 10. Return response
    # -------------------------------------------------

    return {
        "success": True,
        "message": "Document processed and saved successfully.",

        "database_id": document.id,

        "original_filename": file.filename,

        "stored_filename": unique_filename,

        "file_type": validation_result["file_type"],

        "page_count": validation_result["page_count"],

        "extracted_text": extracted_text,

        "structured_result": structured_result,

        "validation": ai_validation_result
    }