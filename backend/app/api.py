from typing import Dict, List, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
import autokeras as ak  # Required for imported AutoKeras custom layers
import numpy as np
import os
import shutil
import joblib
import pickle
import pandas as pd
import json
# from tensorflow.keras.models import load_model # changes depending on Tensorflow version
from tensorflow import keras
from keras.layers import Dense
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler


app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defining Schema
class LoadModelRequest(BaseModel):
    model_name: str



MODEL_DIRECTORY = "./app/models/"
SCALER_DIRECTORY = "./app/scalers/"

os.makedirs(MODEL_DIRECTORY, exist_ok=True)
os.makedirs(SCALER_DIRECTORY, exist_ok=True)

# Store loaded models in memory
loaded_models = {}
loaded_scalers = {}

def load_models():
    """Load available models."""
    return [f for f in os.listdir(MODEL_DIRECTORY) if os.path.isdir(os.path.join(MODEL_DIRECTORY, f))]

@app.get("/models")
def get_models():
    """Get the list of available models."""
    return {"models": load_models()}

@app.post("/upload")
async def upload_model(file: UploadFile = File(...)):
    """Upload and extract a zipped Keras model along with scalers."""
    file_location = os.path.join(MODEL_DIRECTORY, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    model_name = os.path.splitext(file.filename)[0]
    extract_location = os.path.join(MODEL_DIRECTORY, model_name)
    
    shutil.unpack_archive(file_location, extract_location)

    # Move scalers to dedicated directory
    scaler_dir = os.path.join(SCALER_DIRECTORY, model_name)
    os.makedirs(scaler_dir, exist_ok=True)

    try:
        shutil.move(os.path.join(extract_location, "scaler_X.pkl"), os.path.join(scaler_dir, "scaler_X.pkl"))
        shutil.move(os.path.join(extract_location, "scaler_y.pkl"), os.path.join(scaler_dir, "scaler_y.pkl"))
    except Exception as e:
        return {"error": f"Failed to move scalers: {str(e)}"}

    return {"message": "Model uploaded successfully", "model_name": model_name}

@app.post("/load_model")
def load_model_api(data: LoadModelRequest):  
    print(f"Received model_name: {data.model_name}")  # Debugging

    model_name = data.model_name  
    if not model_name:
        raise HTTPException(status_code=400, detail="Model name is required.")

    model_path = os.path.join(MODEL_DIRECTORY, model_name)
    # test scaler
    scaler_x_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_X.pkl")
    scaler_y_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_y.pkl")
    
    if not os.path.exists(model_path):
        return {"error": "Model not found"}

    try:
        model = load_model(model_path, custom_objects=ak.CUSTOM_OBJECTS)
        scaler_X = joblib.load(scaler_x_path)
        scaler_Y = joblib.load(scaler_y_path)
        
        loaded_models[model_name] = model
        loaded_scalers[model_name] = {"scaler_X": scaler_X, "scaler_Y": scaler_Y}

        return {"message": f"Model {model_name} + Scalers loaded successfully!"}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}

# @app.post("/load_model")
# def load_model_api(model_name: str = Form(...)):
#     """Load a model and its scalers dynamically."""
#     model_path = os.path.join(MODEL_DIRECTORY, model_name)
#     scaler_x_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_X.pkl")
#     scaler_y_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_y.pkl")

#     if not os.path.exists(model_path):
#         return {"error": "Model not found"}

#     try:
#         # model = tf.saved_model.load(model_path)
#         model = load_model(model_path, custom_objects=ak.CUSTOM_OBJECTS)
#         scaler_X = joblib.load(scaler_x_path)
#         scaler_Y = joblib.load(scaler_y_path)

#         loaded_models[model_name] = model
#         loaded_scalers[model_name] = {"scaler_X": scaler_X, "scaler_Y": scaler_Y}

#         return {"message": f"Model {model_name} loaded successfully!"}
#     except Exception as e:
#         return {"error": f"Failed to load model: {str(e)}"}

class DynamicInputData(BaseModel):
    model_name: str
    input_data: Dict[str, float]
    input_params: List[str]
    output_params: List[str]

@app.post("/predict")
def predict(data: DynamicInputData):
    """Make a prediction using a dynamically loaded model with defined input/output parameters."""
    print(f"Received Prediction Request: {data}")  # Debugging

    model_name = data.model_name
    input_params = data.input_params
    output_params = data.output_params

    if model_name not in loaded_models:
        return {"error": "Model is not loaded"}

    model = loaded_models[model_name]
    scalers = loaded_scalers.get(model_name, {})

    scaler_X = scalers.get("scaler_X")
    scaler_Y = scalers.get("scaler_Y")

    try:
        # Prepare input data dynamically
        input_values = np.array([[data.input_data.get(param, 0) for param in input_params]])
        print(f"Input values: {input_values}")  # Debugging

        input_df = pd.DataFrame(input_values, columns=input_params)
        input_scaled = scaler_X.transform(input_df)

        raw_prediction = model(input_scaled)
        raw_prediction = raw_prediction.numpy()

        print(f"Raw model output: {raw_prediction}")  # Debugging

        # Inverse scale and format output dynamically
        if scaler_Y:
            prediction_scaled = scaler_Y.inverse_transform(raw_prediction).tolist()[0]
        else:
            prediction_scaled = raw_prediction.tolist()[0]

        result = {output_params[i]: prediction_scaled[i] for i in range(len(output_params))}
        print(f"Final Prediction Result: {result}")  # Debugging

        return {"prediction": result}

    except Exception as e:
        print(f"Prediction Error: {str(e)}")  # Debugging
        return {"error": str(e)}














# from typing import List
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import tensorflow as tf
# import autokeras as ak  # Required for imported AutoKeras custom layers
# import numpy as np
# import json
# import os
# import pickle
# import joblib
# from tensorflow.keras.models import load_model
# from sklearn.preprocessing import MinMaxScaler
# import pandas as pd  # Make sure pandas is imported

# app = FastAPI()

# origins = ["http://localhost:5173"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Define request schema
# class InputData(BaseModel):
#     AmountServer: float
#     Coolingdefect: float
#     InterarrivalTime: float
#     defekteModulanzahl: float

# # Define response schema
# class PredictionResult(BaseModel):
#     AverageServerUtilisation: float
#     AverageFlowTime: float
#     OEE: float
#     TotalAverageQueueLength: float
#     ProcessingTimeAverage: float
#     WaitingTimeAverage: float
#     MovingTimeAverage: float
#     FailedTimeAverage: float
#     BlockedTimeAverage: float
#     Throughput: float

# # Load scaler (you should save and load the same scaler used during training)
# scaler_y = MinMaxScaler()
# scaler_X = MinMaxScaler()

# # Update paths for scalers
# scaler_X_path = "app/scaler_X.pkl"
# scaler_y_path = "app/scaler_y.pkl"

# if os.path.exists(scaler_X_path):
#     scaler_X = joblib.load(scaler_X_path)
#     print("✅ Input scaler loaded successfully!")
# else:
#     print("❌ Warning: No input scaler found.")
#     scaler_X = None

# if os.path.exists(scaler_y_path):
#     scaler_y = joblib.load(scaler_y_path)
#     print("✅ Output scaler loaded successfully!")
# else:
#     print("❌ Warning: No output scaler found.")
#     scaler_y = None

# # Load model
# model_path = os.path.join(os.getcwd(), "app", "project_bayesian", "best_model")
# print("Model Path:", model_path)

# try:
#     model = load_model(model_path, custom_objects=ak.CUSTOM_OBJECTS)
#     print("✅ Model loaded successfully!")
# except Exception as e:
#     print(f"❌ Error loading model: {e}")


# @app.post("/predict", response_model=PredictionResult)
# def predict(data: InputData):
#     try:
#         # Prepare input for prediction (case-sensitive column names)
#         input_data = np.array([[data.AmountServer, data.Coolingdefect, data.InterarrivalTime, data.defekteModulanzahl]])

#         # Debugging: print raw input data
#         print(f"Raw input data: {input_data}")

#         # Create a DataFrame with the exact column names used during training
#         input_data_df = pd.DataFrame(input_data, columns=["AmountServer", "Coolingdefect", "InterarrivalTime", "defekteModulanzahl"])

#         # Debugging: print DataFrame
#         print(f"Input DataFrame: {input_data_df}")

#         # Scale the input data using the scaler_X
#         input_data_normalized = scaler_X.transform(input_data_df)

#         # Debugging: print normalized data
#         print(f"Normalized input data: {input_data_normalized}")

#         # Make prediction
#         raw_prediction = model.predict(input_data_normalized)

#         # Debugging: print raw prediction
#         print(f"Raw prediction: {raw_prediction}")

#         # Inverse transform to original scale if needed
#         if scaler_y:
#             prediction = scaler_y.inverse_transform(raw_prediction).tolist()[0]
#         else:
#             prediction = raw_prediction.tolist()[0]

#         # Debugging: print final prediction
#         print(f"Final prediction: {prediction}")

#         # Structure the response
#         result = {
#             "AverageServerUtilisation": prediction[0],
#             "AverageFlowTime": prediction[1],
#             "OEE": prediction[2],
#             "TotalAverageQueueLength": prediction[3],
#             "ProcessingTimeAverage": prediction[4],
#             "WaitingTimeAverage": prediction[5],
#             "MovingTimeAverage": prediction[6],
#             "FailedTimeAverage": prediction[7],
#             "BlockedTimeAverage": prediction[8],
#             "Throughput": prediction[9]
#         }

#         return result  # Return the result

#     except Exception as e:
#         return {"error": str(e)}



