import os
import json
import numpy as np
from fastapi import APIRouter, HTTPException
from app.services.predict_service import make_prediction
from app.config import MODEL_DIRECTORY, PROCESSED_DIRECTORY
from app.schemas.predict import PredictRequest
from fastapi.responses import JSONResponse

router = APIRouter()

# Function to convert numpy types to regular Python types
def convert_to_python_types(obj):
    if isinstance(obj, np.generic):
        return obj.item()  # Converts numpy types to Python native types
    elif isinstance(obj, dict):
        return {key: convert_to_python_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_types(item) for item in obj]
    return obj

@router.post("/predict/")
def predict_route(data: PredictRequest):
    try:
        # Call the make_prediction function to generate the prediction
        result = make_prediction(data)
        
        # Convert numpy types in the result to Python types
        result = convert_to_python_types(result)
        
        # Return the prediction and output parameters as a response
        return JSONResponse(content={"predictions": result["prediction"]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

@router.get("/predict/processed-files/")
def get_processed_files():
    try:
        # Get all processed files from the PROCESSED_DIRECTORY
        files = os.listdir(PROCESSED_DIRECTORY)
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}

@router.get("/params/{project_name}")
async def get_model_params(project_name: str):
    try:
        # Path to the params.json file
        params_path = os.path.join(PROCESSED_DIRECTORY, project_name, "params.json")
        
        # Check if the params.json exists
        if not os.path.exists(params_path):
            raise HTTPException(status_code=404, detail="Model parameters not found.")
        
        # Load input/output params from params.json
        with open(params_path, "r") as f:
            params = json.load(f)
        
        # Return input params for the frontend to dynamically generate input fields
        return {"input_params": params["input_params"], "output_params": params["output_params"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model parameters: {str(e)}")

# Endpoint to get the available models from the MODEL_DIRECTORY
@router.get("/models")
async def get_models():
    try:
        # List directories under MODEL_DIRECTORY (models)
        models = [
            f for f in os.listdir(MODEL_DIRECTORY)
            if os.path.isdir(os.path.join(MODEL_DIRECTORY, f))  # Only consider directories as models
        ]
        
        return JSONResponse(content={"models": models})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")
