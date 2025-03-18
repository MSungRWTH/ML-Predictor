import os
import joblib
import numpy as np
import json
from fastapi import HTTPException
from app.schemas.predict import PredictRequest
from app.config import MODEL_DIRECTORY, PROCESSED_DIRECTORY
# from tensorflow.keras.models import load_model # changes depending on Tensorflow version
from tensorflow import keras
from keras.layers import Dense
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import logging

# Set up logging
logger = logging.getLogger(__name__)


def make_prediction(data: PredictRequest):
    try:
        # Extract model name and input data from the request
        model_name = data.model_name  # Use model_name here
        input_data = data.input_data
        project_name = data.project_name  # Keep project name for params.json

        # Log received data for debugging
        logger.debug(
            f"Received request for model: {model_name}, project: {project_name}, input data: {input_data}"
        )

        # Paths to the model, scaler, and parameters
        model_dir = MODEL_DIRECTORY / model_name
        scaler_dir = PROCESSED_DIRECTORY / project_name
        model_path = model_dir / "best_model"

        # Log the model path for debugging
        logger.debug(f"Model path: {model_path}")

        # Check if model exists
        if not model_path.exists():
            logger.error(f"Model file does not exist at {model_path}")
            raise HTTPException(status_code=400, detail="Model file does not exist.")

        # Load the trained model
        model = keras.models.load_model(model_path)

        # Load the scalers for input and output
        scaler_X = joblib.load(scaler_dir / "scaler_X.pkl")
        scaler_y = joblib.load(scaler_dir / "scaler_y.pkl")

        # Load input/output parameters from the params.json file
        params_path = PROCESSED_DIRECTORY / project_name / "params.json"

        # Log the params path for debugging
        logger.debug(f"Params path: {params_path}")

        # Check if params file exists
        if not params_path.exists():
            logger.error(f"Parameters file does not exist at {params_path}")
            raise HTTPException(
                status_code=400, detail="Parameters file does not exist."
            )

        # Load the parameters from the JSON file
        with params_path.open() as f:
            params = json.load(f)

        # Extract input and output parameters
        input_params = params.get("input_params", [])
        output_params = params.get("output_params", [])

        # Ensure input data matches the expected structure
        input_values = [input_data[param] for param in input_params]

        # Scale the input data using the scaler
        input_scaled = scaler_X.transform(np.array([input_values]))

        # Make the prediction using the model
        prediction_scaled = model.predict(input_scaled)

        # Inverse scale the prediction
        prediction = scaler_y.inverse_transform(prediction_scaled)

        # Return the prediction as a dictionary with output parameters
        return {
            "prediction": {
                output_params[i]: prediction[0][i] for i in range(len(output_params))
            }
        }

    except Exception as e:
        logger.exception(f"Error during prediction: {e!s}")
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e!s}")
