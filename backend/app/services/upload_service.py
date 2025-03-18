import os
import json
import logging
import pandas as pd 
import ast
import shutil
from fastapi import UploadFile, HTTPException
from app.config import UPLOAD_DIRECTORY

async def handle_upload(file: UploadFile):
    try:
        # Ensure the file is either JSON or CSV
        if (
            file.filename is None
            or not file.filename.endswith(".json")
            or not file.filename.endswith(".csv")
        ):
            raise HTTPException(
                status_code=400, detail="Only JSON or CSV files are allowed."
            )

        # Save the uploaded file to the directory
        file_location = UPLOAD_DIRECTORY / file.filename

        with file_location.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        return {"message": f"File {file.filename} uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
