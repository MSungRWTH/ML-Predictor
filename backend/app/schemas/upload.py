from pydantic import BaseModel
from typing import Optional

class UploadRequest(BaseModel):
    """
    Schema for the JSON upload request.
    """
    file: str

class UploadResponse(BaseModel):
    """
    Schema for the JSON upload response.
    """
    message: str        # Success or error message
    project_name: str   # Name of the project where the files are saved