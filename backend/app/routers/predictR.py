import os
import json
from fastapi import APIRouter, HTTPException
from app.services.predict_service import make_prediction
from app.schemas.predict import PredictRequest
from app.config import MODEL_DIRECTORY
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("/")
def predict_route(data: PredictRequest):
    return make_prediction(data)


@router.get("/params/{project_name}")
async def get_model_params(project_name: str):
    try:
        # Path to the params.json file
        model_dir = os.path.join(MODEL_DIRECTORY, f"{project_name}_model")
        params_path = os.path.join(model_dir, "params.json")
        
        # Check if the params.json exists
        if not os.path.exists(params_path):
            raise HTTPException(status_code=404, detail="Model parameters not found.")
        
        # Load input/output params from params.json
        with open(params_path, "r") as f:
            params = json.load(f)
        
        # Return input params for the frontend to dynamically generate input fields
        return {"input_params": params["input_params"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model parameters: {str(e)}")


# Endpoint to get the available models from the MODEL_DIRECTORY
@router.get("/models")
async def get_models():
    try:
        # Ensure the model directory exists
        if not os.path.exists(MODEL_DIRECTORY):
            raise FileNotFoundError(f"Model directory '{MODEL_DIRECTORY}' does not exist.")
        
        # List directories under MODEL_DIRECTORY
        models = [
            f for f in os.listdir(MODEL_DIRECTORY)
            if os.path.isdir(os.path.join(MODEL_DIRECTORY, f))  # Only consider directories
        ]
        
        # If no models are found
        if not models:
            raise ValueError("No models found in the directory.")
        
        return JSONResponse(content={"models": models})
    
    except Exception as e:
        # Log the exception details for better debugging
        print(f"Error fetching models: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

