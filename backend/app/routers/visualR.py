import os
import json
from fastapi import APIRouter, HTTPException
from app.config import MODEL_DIRECTORY


router = APIRouter()

@router.get("/models")
def list_models():
    """Returns a list of available models in MODEL_DIRECTORY."""
    try:
        models = [d for d in os.listdir(MODEL_DIRECTORY) if os.path.isdir(os.path.join(MODEL_DIRECTORY, d))]
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/{model_name}")
def get_model_visualization_data(model_name: str):
    """Fetches MAE vs. Trials and MAE vs. Training Time data for the selected model."""
    model_path = os.path.join(MODEL_DIRECTORY, model_name)
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not found")

    trial_mae = []
    training_time = None

    # Load training time
    training_time_path = os.path.join(model_path, "training_time.json")
    if os.path.exists(training_time_path):
        with open(training_time_path, "r") as f:
            training_time_data = json.load(f)
            training_time = training_time_data.get("training_time", None)

    # Load trial MAE values
    for trial_dir in sorted(os.listdir(model_path)):
        trial_path = os.path.join(model_path, trial_dir, "trial.json")
        if os.path.exists(trial_path):
            try:
                with open(trial_path, "r") as f:
                    trial_data = json.load(f)
                    val_loss_observations = trial_data.get("metrics", {}).get("metrics", {}).get("val_loss", {}).get("observations", [])
                    if val_loss_observations:
                        val_loss_value = val_loss_observations[0].get("value", [])
                        if val_loss_value:
                            trial_mae.append(val_loss_value[0])
            except json.JSONDecodeError:
                continue

    if not trial_mae:
        raise HTTPException(status_code=400, detail="No valid MAE data found for the model")

    return {
        "trial_mae": trial_mae,
        "training_time": training_time
    }
