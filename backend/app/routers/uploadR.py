from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.upload_service import handle_upload
from app.schemas.upload import UploadRequest

# Handles routes for uploading JSON files and defining input/out features

# Define the router
router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    return await handle_upload(file)