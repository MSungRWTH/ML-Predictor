from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.automl import AutoMLRegressor
from app.schemas.train import TrainRequest, TrainResponse
from app.config import PROCESSED_DIRECTORY, MODEL_DIRECTORY
import os
import json
import logging
from typing import List
from concurrent.futures import ProcessPoolExecutor, as_completed

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)

# Function to train the model for a given tuner
def train_model(tuner_type, request, project_path, train_data_file, scaler_x_file, scaler_y_file):
    """Function to train the model for a given tuner type."""
    try:
        model_path = os.path.join(MODEL_DIRECTORY, request.project_name)
        os.makedirs(model_path, exist_ok=True)
        
        regressor = AutoMLRegressor(
            train_data_path=train_data_file,
            scaler_x_path=scaler_x_file,
            scaler_y_path=scaler_y_file,
            tuner_types=[tuner_type],
            project_name=request.project_name
        )
        
        regressor.load_train_data()
        regressor.train_model(tuner_type)
    except Exception as e:
        logger.error(f"Training failed for {tuner_type} on {request.project_name}: {e}")
        raise e

@router.get("/projects/", response_model=List[str])
def get_projects():
    """List available projects in PROCESSED_DIRECTORY."""
    try:
        projects = [d for d in os.listdir(PROCESSED_DIRECTORY) if os.path.isdir(os.path.join(PROCESSED_DIRECTORY, d))]
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/train/processed-files/")  # Get list of processed files
def get_processed_files():
    try:
        files = os.listdir(PROCESSED_DIRECTORY)
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}

@router.get("/train/get-params/{project_name}")  # Get parameters for a specific project
def get_params(project_name: str):
    """Fetch input and output parameters for a specific project."""
    project_path = os.path.join(PROCESSED_DIRECTORY, project_name)
    params_file = os.path.join(project_path, "params.json")
    
    if not os.path.exists(params_file):
        raise HTTPException(status_code=404, detail=f"params.json not found for {project_name}")
    
    try:
        with open(params_file, "r") as f:
            params = json.load(f)
        input_params = params.get("input_params", [])
        output_params = params.get("output_params", [])
        return {"input_params": input_params, "output_params": output_params}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train/")  # Start training for the selected project
def start_training(request: TrainRequest):
    """Start training for the selected project."""
    project_path = os.path.join(PROCESSED_DIRECTORY, request.project_name)
    model_path = os.path.join(MODEL_DIRECTORY, request.project_name)
    params_file = os.path.join(project_path, "params.json")
    train_data_file = os.path.join(project_path, "train_data.npz")
    scaler_x_file = os.path.join(project_path, "scaler_X.pkl")
    scaler_y_file = os.path.join(project_path, "scaler_y.pkl")
    
    if not os.path.exists(params_file):
        raise HTTPException(status_code=400, detail=f"params.json not found for {request.project_name}")
    if not os.path.exists(train_data_file):
        raise HTTPException(status_code=400, detail=f"train_data.npz not found for {request.project_name}")
    
    os.makedirs(model_path, exist_ok=True)
    
    # Load input/output parameters
    try:
        with open(params_file, "r") as f:
            params = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load params.json for {request.project_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading parameters: {e}")
    
    # Run training in parallel for all tuners if the tuner is 'all'
    if request.tuner == "all":
        tuner_types = ['random', 'hyperband', 'greedy', 'bayesian']
    else:
        tuner_types = [request.tuner]
    
    try:
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(train_model, tuner, request, project_path, train_data_file, scaler_x_file, scaler_y_file): tuner
                for tuner in tuner_types
            }
            for future in as_completed(futures):
                try:
                    future.result()  # Wait for completion
                except Exception as exc:
                    logger.error(f"Error during training: {exc}")
                    raise HTTPException(status_code=500, detail=f"Error in {futures[future]}: {exc}")
    except Exception as e:
        logger.error(f"Training process failed for {request.project_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")
    
    return {"message": f"Training started for {request.project_name} with tuner(s): {', '.join(tuner_types)}"}
