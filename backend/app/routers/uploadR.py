from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import json
import pandas as pd
from app.schemas.upload import PreprocessRequest
from app.services.upload_service import handle_upload
from app.services.data_preprocessor import DataPreprocessor  # Import the new service
from app.config import UPLOAD_DIRECTORY, PROCESSED_DIRECTORY

router = APIRouter()

# Upload a new file
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save file to the UPLOAD_DIRECTORY
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

# List available datasets in UPLOAD_DIRECTORY
@router.get("/files/", response_model=List[str])
def list_datasets():
    try:
        return [f for f in os.listdir(UPLOAD_DIRECTORY) if f.endswith(('.json', '.csv'))]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch column names from the selected file
@router.get("/get_columns/")
def get_columns(file_name: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    df = pd.read_csv(file_path) if file_name.endswith(".csv") else pd.read_json(file_path)
    return {"columns": df.columns.tolist()}

# Save selected input/output parameters
@router.post("/save_params/")
async def save_params(request: PreprocessRequest):  # Accept the body as PreprocessRequest schema
    try:
        # Define the directory where parameters will be saved
        project_dir = os.path.join(PROCESSED_DIRECTORY, request.project_name)
        
        # Create the directory if it doesn't exist
        os.makedirs(project_dir, exist_ok=True)

        # Prepare the parameters to be saved
        params = {
            "input_params": request.input_params,
            "output_params": request.output_params,
            "file_name": request.file_name
        }

        # Save the parameters to a JSON file
        params_file_path = os.path.join(project_dir, "params.json")
        with open(params_file_path, "w") as f:
            json.dump(params, f)
        
        # Return a success message
        return {"message": "Parameters saved successfully.", "file_path": params_file_path}
    
    except Exception as e:
        # If an error occurs, return an error message
        raise HTTPException(status_code=500, detail=f"Error saving parameters: {str(e)}")


# New: Call the DataPreprocessor class for preprocessing
@router.post("/preprocess/")
async def preprocess_data(request: PreprocessRequest):
    try:
        # Ensure required fields are provided
        if not request.project_name or not request.input_params or not request.output_params:
            raise HTTPException(status_code=400, detail="Missing required parameters.")

        # Log the received request data for debugging
        print(f"Preprocessing request received with data: {request}")

        # Instantiate the DataPreprocessor with project name, scaler type, and parameters
        preprocessor = DataPreprocessor(
            project_name=request.project_name,
            scaler_type=request.scaler_type,  # Assuming scaler_type is part of PreprocessRequest schema
            input_params=request.input_params,
            output_params=request.output_params,
            file_name=request.file_name
        )

        # Call preprocess method from DataPreprocessor
        result = preprocessor.preprocess()

        # Log the result of preprocessing for debugging
        print(f"Preprocessing result: {result}")

        return {"message": "Preprocessing successful", "data": result}
    
    except HTTPException as http_error:
        # Catch HTTP exceptions and raise them with the appropriate status code
        raise http_error
    except Exception as e:
        # Log the exception to the console for debugging purposes
        print(f"Error in preprocessing: {str(e)}")

        # Raise a 500 HTTPException with the error details
        raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")

