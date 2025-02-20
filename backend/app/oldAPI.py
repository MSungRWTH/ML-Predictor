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

# Defining Input Class
class DynamicInputData(BaseModel):
    model_name: str
    input_data: Dict[str, float]
    input_params: List[str]
    output_params: List[str]

class PredictionRequest(BaseModel):
    model_name: str
    input_data: Dict[str, float]

# Define Directories
MODEL_DIRECTORY = "./app/models/"
SCALER_DIRECTORY = "./app/scalers/"

os.makedirs(MODEL_DIRECTORY, exist_ok=True)
os.makedirs(SCALER_DIRECTORY, exist_ok=True)

# Store loaded models and scalers
loaded_models = {}
loaded_scalers = {}
loaded_metadata = {}  # Store input/output parameter names dynamically


class LoadModelRequest(BaseModel):
    model_name: str


@app.get("/models")
def get_models():
    """Get the list of available models."""
    return {"models": [f for f in os.listdir(MODEL_DIRECTORY) if os.path.isdir(os.path.join(MODEL_DIRECTORY, f))]}



# might be implemented in the future, for possibility to upload a model from frontend
# @app.post("/upload")
# async def upload_model(file: UploadFile = File(...)):
#     """Upload and extract a zipped Keras model along with scalers."""
#     file_location = os.path.join(MODEL_DIRECTORY, file.filename)
#     with open(file_location, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     model_name = os.path.splitext(file.filename)[0]
#     extract_location = os.path.join(MODEL_DIRECTORY, model_name)

#     shutil.unpack_archive(file_location, extract_location)

#     # Move scalers to dedicated directory
#     scaler_dir = os.path.join(SCALER_DIRECTORY, model_name)
#     os.makedirs(scaler_dir, exist_ok=True)

#     try:
#         shutil.move(os.path.join(extract_location, "scaler_X.pkl"), os.path.join(scaler_dir, "scaler_X.pkl"))
#         shutil.move(os.path.join(extract_location, "scaler_y.pkl"), os.path.join(scaler_dir, "scaler_y.pkl"))
#     except Exception:
#         pass  # Ignore if scalers are not found

#     return {"message": "Model uploaded successfully", "model_name": model_name}


@app.post("/load_model")
def load_model_api(data: LoadModelRequest):
    """Load a model and extract input/output parameter names dynamically."""
    model_name = data.model_name
    model_path = os.path.join(MODEL_DIRECTORY, model_name)

    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not found.")

    try:
        # Debugging: Print path
        print(f"Loading model from: {model_path}")

        model = load_model(model_path, custom_objects=ak.CUSTOM_OBJECTS)

        # Debugging: Model structure
        print(f"Model loaded successfully: {model.summary()}")

        scaler_X_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_X.pkl")
        scaler_Y_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_y.pkl")

        scaler_X, scaler_Y = None, None
        if os.path.exists(scaler_X_path):
            scaler_X = joblib.load(scaler_X_path)
            print("Scaler X loaded successfully")
        if os.path.exists(scaler_Y_path):
            scaler_Y = joblib.load(scaler_Y_path)
            print("Scaler Y loaded successfully")

        loaded_models[model_name] = model
        loaded_scalers[model_name] = {"scaler_X": scaler_X, "scaler_Y": scaler_Y}

        # Extract input & output parameters dynamically, all problems here
        input_params = [layer["config"]["name"] for layer in model.get_config()["layers"] if layer["class_name"] == "InputLayer"]
        output_params = [layer["config"]["name"] for layer in model.get_config()["layers"] if "output" in layer["config"]["name"].lower()]



        loaded_metadata[model_name] = {
            "input_params": input_params,
            "output_params": output_params
        }

        print(f"Extracted input params: {input_params}")
        print(f"Extracted output params: {output_params}")

        return {"message": f"Model {model_name} + Scalers loaded successfully!"}

    except Exception as e:
        print(f"Error loading model {model_name}: {str(e)}")  # Debugging
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


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
        input_values = np.expand_dims(input_values, axis=0)  # Ensure batch dimension is added
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




# from typing import Dict, List, Any
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import tensorflow as tf
# import autokeras as ak  # Required for imported AutoKeras custom layers
# import numpy as np
# import os
# import shutil
# import joblib
# import pickle
# import pandas as pd
# import json
# # from tensorflow.keras.models import load_model # changes depending on Tensorflow version
# from tensorflow import keras
# from keras.layers import Dense
# from keras.models import Sequential, load_model
# from sklearn.preprocessing import MinMaxScaler


# app = FastAPI()

# origins = ["http://localhost:5173"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Defining Schema
# class LoadModelRequest(BaseModel):
#     model_name: str



# MODEL_DIRECTORY = "./app/models/"
# SCALER_DIRECTORY = "./app/scalers/"

# os.makedirs(MODEL_DIRECTORY, exist_ok=True)
# os.makedirs(SCALER_DIRECTORY, exist_ok=True)

# # Store loaded models in memory
# loaded_models = {}
# loaded_scalers = {}

# def load_models():
#     """Load available models."""
#     return [f for f in os.listdir(MODEL_DIRECTORY) if os.path.isdir(os.path.join(MODEL_DIRECTORY, f))]

# @app.get("/models")
# def get_models():
#     """Get the list of available models."""
#     return {"models": load_models()}

# @app.get("/model_info/{model_name}")
# def get_model_info(model_name: str):
#     """Retrieve the input and output parameters for a loaded model."""
#     if model_name not in loaded_models:
#         raise HTTPException(status_code=404, detail="Model not found or not loaded.")

#     try:
#         model = loaded_models[model_name]
#         input_params = model.input_names  # Extract input names
#         output_params = [node.name for node in model.output]  # Extract output names

#         return {
#             "input_params": input_params,
#             "output_params": output_params,
#         }
#     except Exception as e:
#         return {"error": f"Failed to retrieve model info: {str(e)}"}

# @app.post("/upload")
# async def upload_model(file: UploadFile = File(...)):
#     """Upload and extract a zipped Keras model along with scalers."""
#     file_location = os.path.join(MODEL_DIRECTORY, file.filename)
#     with open(file_location, "wb") as f:
#         shutil.copyfileobj(file.file, f)
    
#     model_name = os.path.splitext(file.filename)[0]
#     extract_location = os.path.join(MODEL_DIRECTORY, model_name)
    
#     shutil.unpack_archive(file_location, extract_location)

#     # Move scalers to dedicated directory
#     scaler_dir = os.path.join(SCALER_DIRECTORY, model_name)
#     os.makedirs(scaler_dir, exist_ok=True)

#     try:
#         shutil.move(os.path.join(extract_location, "scaler_X.pkl"), os.path.join(scaler_dir, "scaler_X.pkl"))
#         shutil.move(os.path.join(extract_location, "scaler_y.pkl"), os.path.join(scaler_dir, "scaler_y.pkl"))
#     except Exception as e:
#         return {"error": f"Failed to move scalers: {str(e)}"}

#     return {"message": "Model uploaded successfully", "model_name": model_name}

# @app.post("/load_model")
# def load_model_api(data: LoadModelRequest):  
#     print(f"Received model_name: {data.model_name}")  # Debugging

#     model_name = data.model_name  
#     if not model_name:
#         raise HTTPException(status_code=400, detail="Model name is required.")

#     model_path = os.path.join(MODEL_DIRECTORY, model_name)
#     # test scaler
#     scaler_x_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_X.pkl")
#     scaler_y_path = os.path.join(SCALER_DIRECTORY, model_name, "scaler_y.pkl")
    
#     if not os.path.exists(model_path):
#         return {"error": "Model not found"}

#     try:
#         model = load_model(model_path, custom_objects=ak.CUSTOM_OBJECTS)
#         scaler_X = joblib.load(scaler_x_path)
#         scaler_Y = joblib.load(scaler_y_path)
        
#         loaded_models[model_name] = model
#         loaded_scalers[model_name] = {"scaler_X": scaler_X, "scaler_Y": scaler_Y}

#         return {"message": f"Model {model_name} + Scalers loaded successfully!"}
#     except Exception as e:
#         return {"error": f"Failed to load model: {str(e)}"}
    
# class DynamicInputData(BaseModel):
#     model_name: str
#     input_data: Dict[str, float]
#     input_params: List[str]
#     output_params: List[str]

# @app.post("/predict")
# def predict(data: DynamicInputData):
#     """Make a prediction using a dynamically loaded model with defined input/output parameters."""
#     print(f"Received Prediction Request: {data}")  # Debugging

#     model_name = data.model_name
#     input_params = data.input_params
#     output_params = data.output_params

#     if model_name not in loaded_models:
#         return {"error": "Model is not loaded"}

#     model = loaded_models[model_name]
#     scalers = loaded_scalers.get(model_name, {})

#     scaler_X = scalers.get("scaler_X")
#     scaler_Y = scalers.get("scaler_Y")

#     try:
#         # Prepare input data dynamically
#         input_values = np.array([[data.input_data.get(param, 0) for param in input_params]])
#         print(f"Input values: {input_values}")  # Debugging

#         input_df = pd.DataFrame(input_values, columns=input_params)
#         input_scaled = scaler_X.transform(input_df)

#         raw_prediction = model(input_scaled)
#         raw_prediction = raw_prediction.numpy()

#         print(f"Raw model output: {raw_prediction}")  # Debugging

#         # Inverse scale and format output dynamically
#         if scaler_Y:
#             prediction_scaled = scaler_Y.inverse_transform(raw_prediction).tolist()[0]
#         else:
#             prediction_scaled = raw_prediction.tolist()[0]

#         result = {output_params[i]: prediction_scaled[i] for i in range(len(output_params))}
#         print(f"Final Prediction Result: {result}")  # Debugging

#         return {"prediction": result}

#     except Exception as e:
#         print(f"Prediction Error: {str(e)}")  # Debugging
#         return {"error": str(e)}








