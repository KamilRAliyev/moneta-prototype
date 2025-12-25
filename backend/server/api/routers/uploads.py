"""File upload endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from server.core.logging import get_logger
from server.services import data_dir

logger = get_logger(__name__)

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV file.

    Saves the file to /data/uploads/{uuid}.csv without any parsing or validation.

    Args:
        file: The uploaded file

    Returns:
        JSON response with file ID and path
    """
    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Ensure uploads directory exists
    uploads_dir = data_dir.ensure_uploads_dir()

    # Construct file path
    file_path = uploads_dir / f"{file_id}.csv"

    try:
        # Read file content
        content = await file.read()

        # Write to disk
        file_path.write_bytes(content)

        logger.info(
            f"File uploaded successfully",
            extra={
                "file_id": file_id,
                "uploaded_filename": file.filename,
                "size": len(content),
                "path": str(file_path),
            },
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "file_id": file_id,
                "path": str(file_path),
                "filename": file.filename,
            },
        )
    except Exception as e:
        logger.error(
            f"Error uploading file: {str(e)}",
            exc_info=True,
            extra={"file_id": file_id, "uploaded_filename": file.filename},
        )
        raise
