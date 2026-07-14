from fastapi import APIRouter

router = APIRouter()

from . import detection, tracking, upload  # noqa: F401
