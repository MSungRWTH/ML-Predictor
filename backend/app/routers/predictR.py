
import json
import numpy as np
from fastapi import APIRouter, HTTPException
from app.services.predict_service import make_prediction
from app.config import MODEL_DIRECTORY, PROCESSED_DIRECTORY
from app.schemas.predict import PredictRequest
from fastapi.responses import JSONResponse

from keras.models import load_model
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import logging


logger = logging.getLogger(__name__)


router = APIRouter()

# Function to convert numpy types to regular Python types
def convert_to_python_types(obj):
    if isinstance(obj, np.generic):
        return obj.item()  # Converts numpy types to Python native types
    if isinstance(obj, dict):
        return {key: convert_to_python_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_to_python_types(item) for item in obj]
    return obj


@router.get("/metrics/{model_name}")
def compute_model_metrics(model_name: str, project_name: str):
    """
    Computes MAE, R², and MAPE dynamically for a given model.
    Computes metrics for each output feature in the model.
    """

    model_path = MODEL_DIRECTORY / model_name
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    processed_project_path = PROCESSED_DIRECTORY / project_name

    # Load the best model
    try:
        best_model = load_model(model_path / "best_model")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail="Failed to load model")

    # Load the test dataset
    test_data_path = processed_project_path / "test_data.npz"
    if not test_data_path.exists():
        raise HTTPException(status_code=404, detail="Test dataset not found")

    try:
        data = np.load(test_data_path)
        X_test = data["X_test"]
        y_test = data["y_test"]
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load test data")

    # Load the scaler for inverse transformation
    scaler_path = processed_project_path / "scaler_y.pkl"
    if not scaler_path.exists():
        raise HTTPException(status_code=404, detail="Scaler file not found")

    try:
        with open(scaler_path, "rb") as f:
            scaler_y = pickle.load(f)

        predictions = best_model.predict(X_test)

        # Ensure correct shape for inverse transformation
        if predictions.ndim == 1:
            predictions = predictions.reshape(-1, 1)
        if y_test.ndim == 1:
            y_test = y_test.reshape(-1, 1)

        predictions_inverse = scaler_y.inverse_transform(predictions)
        y_test_inverse = scaler_y.inverse_transform(y_test)

    except Exception as e:
        logger.error(f"Error applying inverse scaling: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply inverse scaling")

    # Load output_params from params.json for naming features
    params_path = processed_project_path / "params.json"
    if not params_path.exists():
        raise HTTPException(status_code=404, detail="params.json file not found")

    try:
        with open(params_path, "r") as f:
            params = json.load(f)
        output_params = params.get("output_params", [])
    except Exception as e:
        logger.error(f"Error loading output_params: {e}")
        raise HTTPException(status_code=500, detail="Failed to load output parameters")

    # Compute Metrics for all outputs
    epsilon = 1e-6  # Small constant to prevent division by near-zero values
    metrics = {}
    for i, feature_name in enumerate(output_params):  # Use correct feature names
        if i >= y_test_inverse.shape[1]:  # Safety check
            break

        # Calculate MAE, R², and MAPE for each output feature
        feature_mae = mean_absolute_error(y_test_inverse[:, i], predictions_inverse[:, i])
        feature_r2 = r2_score(y_test_inverse[:, i], predictions_inverse[:, i])

        non_zero_indices_feature = np.abs(y_test_inverse[:, i]) > epsilon  # Avoid near-zero issues
        if np.any(non_zero_indices_feature):
            feature_mape = np.mean(
                np.abs((y_test_inverse[non_zero_indices_feature, i] - predictions_inverse[non_zero_indices_feature, i]) /
                       np.maximum(y_test_inverse[non_zero_indices_feature, i], epsilon))) * 100
        else:
            feature_mape = float('nan')

        # Replace NaN or infinite values with None
        metrics[feature_name] = {
            "mae": None if np.isnan(feature_mae) or np.isinf(feature_mae) else feature_mae,
            "r2": None if np.isnan(feature_r2) or np.isinf(feature_r2) else feature_r2,
            "mape": None if np.isnan(feature_mape) or np.isinf(feature_mape) else feature_mape
        }

    # Overall Metrics
    overall_mae = mean_absolute_error(y_test_inverse, predictions_inverse)
    overall_r2 = r2_score(y_test_inverse, predictions_inverse)

    non_zero_indices = np.abs(y_test_inverse) > epsilon
    if np.any(non_zero_indices):
        overall_mape = np.mean(
            np.abs((y_test_inverse[non_zero_indices] - predictions_inverse[non_zero_indices]) /
                   np.maximum(y_test_inverse[non_zero_indices], epsilon))) * 100
    else:
        overall_mape = float("nan")

    # Replace NaN or infinite values with None
    metrics["Overall"] = {
        "mae": None if np.isnan(overall_mae) or np.isinf(overall_mae) else overall_mae,
        "r2": None if np.isnan(overall_r2) or np.isinf(overall_r2) else overall_r2,
        "mape": None if np.isnan(overall_mape) or np.isinf(overall_mape) else overall_mape
    }

    return metrics


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
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e!s}")


@router.get("/predict/processed-files/")
def get_processed_files():
    try:
        # Get all processed files from the PROCESSED_DIRECTORY
        files = [str(f.name) for f in PROCESSED_DIRECTORY.iterdir()]
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}


@router.get("/params/{project_name}")
async def get_model_params(project_name: str):
    try:
        # Path to the params.json file
        params_path = PROCESSED_DIRECTORY / project_name / "params.json"

        # Check if the params.json exists
        if not params_path.exists():
            raise HTTPException(status_code=404, detail="Model parameters not found.")

        # Load input/output params from params.json
        with params_path.open() as f:
            params = json.load(f)

        # Return input params for the frontend to dynamically generate input fields
        return {
            "input_params": params["input_params"],
            "output_params": params["output_params"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model parameters: {e!s}")


# Endpoint to get the available models from the MODEL_DIRECTORY
@router.get("/models")
async def get_models():
    try:
        # List directories under MODEL_DIRECTORY (models)
        models = [str(d.name) for d in MODEL_DIRECTORY.iterdir() if d.is_dir()]

        return {"models": models}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {e!s}")

