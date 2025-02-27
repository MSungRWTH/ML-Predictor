from pydantic import BaseModel
from typing import Optional, List, Literal

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
    
class PreprocessRequest(BaseModel):
    project_name: str  # Name of the project
    input_params: List[str]  # List of selected input columns
    output_params: List[str]  # List of selected output columns
    file_name: str  # Name of the selected dataset
    scaler_type: Literal['StandardScaler', 'MinMaxScaler']  # Ensures only these two values are allowed

class PreprocessResponse(BaseModel):
    message: str  # Success message
    processed_data_preview: dict  # Sample of preprocessed data 