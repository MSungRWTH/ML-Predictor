from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.automl import AutoMLRegressor
from app.schemas.train import TrainRequest, TrainResponse
from app.config import PROCESSED_DIRECTORY, MODEL_DIRECTORY
import json
import logging
from typing import List
from concurrent.futures import ProcessPoolExecutor, as_completed

router = APIRouter()

logger = logging.getLogger(__name__)

# Function to train the model for a given tuner
def train_model(tuner_type, project_name, train_data_file, scaler_x_file, scaler_y_file, no_trials, no_epochs):
    """Train the model for a given tuner type."""
    try:
        model_path = MODEL_DIRECTORY / f"{project_name}_{tuner_type}"
        if not model_path.exists():
            model_path.mkdir(parents=True)

        regressor = AutoMLRegressor(
            train_data_path=train_data_file,
            scaler_x_path=scaler_x_file,
            scaler_y_path=scaler_y_file,
            tuner_types=[tuner_type],
            project_name=project_name,
            no_trials=no_trials,
            no_epochs=no_epochs,
        )

        regressor.load_train_data()
        regressor.train_automl_model(tuner_type)
    except Exception as e:
        logger.error(f"Training failed for {tuner_type} on {project_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed for {tuner_type}: {e}")

@router.get("/projects/", response_model=list[str])
def get_projects():
    """List available projects in PROCESSED_DIRECTORY."""
    try:
        return [str(d.name) for d in PROCESSED_DIRECTORY.iterdir() if d.is_dir()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/train/processed-files/")
def get_processed_files():
    """Get a list of processed files."""
    try:
        files = [str(f.name) for f in PROCESSED_DIRECTORY.iterdir()]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {e}")

@router.get("/train/get-params/{project_name}")
def get_params(project_name: str):
    """Fetch input and output parameters for a specific project."""
    project_path = PROCESSED_DIRECTORY / project_name
    params_file = project_path / "params.json"

    if not params_file.exists():
        raise HTTPException(status_code=404, detail=f"params.json not found for {project_name}")

    try:
        with params_file.open() as f:
            params = json.load(f)
        input_params = params.get("input_params", [])
        output_params = params.get("output_params", [])
        return {"input_params": input_params, "output_params": output_params}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading parameters: {e}")

@router.post("/train/")
def start_training(request: TrainRequest):
    """Start training for the selected project."""
    logger.info(f"Received request: {request}")
    project_path = PROCESSED_DIRECTORY / request.project_name
    model_path = MODEL_DIRECTORY / f"{request.project_name}_{request.tuner}"
    params_file = project_path / "params.json"
    train_data_file = project_path / "train_data.npz"
    scaler_x_file = project_path / "scaler_X.pkl"
    scaler_y_file = project_path / "scaler_y.pkl"

    if not params_file.exists():
        raise HTTPException(status_code=400, detail=f"params.json not found for {request.project_name}")
    if not train_data_file.exists():
        raise HTTPException(status_code=400, detail=f"train_data.npz not found for {request.project_name}")
    if not scaler_x_file.exists() or not scaler_y_file.exists():
        raise HTTPException(status_code=400, detail=f"Scaler files not found for {request.project_name}")

    # Create model directory if not exists
    if not model_path.exists():
        model_path.mkdir(parents=True)

    # Load input/output parameters
    try:
        with params_file.open() as f:
            params = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load params.json for {request.project_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading parameters: {e}")

    # Run training for all tuners if 'all' is selected
    tuner_types = ["random", "hyperband", "greedy", "bayesian"] if request.tuner == "all" else [request.tuner]

    try:
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(
                    train_model,
                    tuner,
                    request.project_name,  # Pass project_name as argument
                    train_data_file,
                    scaler_x_file,
                    scaler_y_file,
                    request.no_trials,  # Pass no_trials as argument
                    request.no_epochs,  # Pass no_epochs as argument
                ): tuner
                for tuner in tuner_types
            }
            for future in as_completed(futures):
                try:
                    future.result()  # Wait for completion
                except Exception as exc:
                    logger.error(f"Error during training: {exc}")
                    raise HTTPException(status_code=500, detail=f"Error during training with {futures[future]}: {exc}")
    except Exception as e:
        logger.error(f"Training process failed for {request.project_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

    return {"message": f"Training finished for {request.project_name} with tuner(s): {', '.join(tuner_types)}"}












