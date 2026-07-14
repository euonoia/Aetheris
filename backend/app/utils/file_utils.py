import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import UPLOAD_DIR


def save_uploaded_file(file: UploadFile, allowed_prefixes: list[str], error_detail: str) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.content_type or not any(file.content_type.startswith(prefix) for prefix in allowed_prefixes):
        raise HTTPException(status_code=400, detail=error_detail)

    extension = os.path.splitext(file.filename)[1] or ".bin"
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path
