from fastapi import APIRouter, File, UploadFile
from .detection import detect_image

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await detect_image(file)
