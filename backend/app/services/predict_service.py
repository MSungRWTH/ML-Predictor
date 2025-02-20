import os
import joblib
import numpy as np
import json
from fastapi import HTTPException
from app.schemas.predict import PredictRequest
from app.config import MODEL_DIRECTORY
# from tensorflow.keras.models import load_model # changes depending on Tensorflow version
from tensorflow import keras
from keras.layers import Dense
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler

def make_prediction(data: PredictRequest):
    try:
        project_name = data.project_name
        input_data = data.input_data

        # Load model and scalers
        model_dir = os.path.join(MODEL_DIRECTORY, f"{project_name}_model")
        model_path = os.path.join(model_dir, "model.h5")
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=400, detail="Model file does not exist.")
        
        model = load_model(model_path)
        scaler_X = joblib.load(os.path.join(model_dir, "scaler_X.pkl"))
        scaler_y = joblib.load(os.path.join(model_dir, "scaler_y.pkl"))

        # Load input/output parameters
        params_path = os.path.join(model_dir, "params.json")
        if not os.path.exists(params_path):
            raise HTTPException(status_code=400, detail="Parameters file does not exist.")
        
        with open(params_path, "r") as f:
            params = json.load(f)
        
        input_params = params["input_params"]
        output_params = params["output_params"]

        # Ensure input data matches the expected structure
        input_scaled = scaler_X.transform(np.array([list(input_data.values())]))

        # Make prediction
        prediction_scaled = model.predict(input_scaled)
        prediction = scaler_y.inverse_transform(prediction_scaled)

        return {
            "prediction": prediction.tolist(),
            "input_params": input_params,
            "output_params": output_params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")
