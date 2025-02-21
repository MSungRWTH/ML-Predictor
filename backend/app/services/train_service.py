from fastapi import FastAPI, HTTPException, UploadFile, File
import os
import json
import pandas as pd
from typing import List
from pydantic import BaseModel
import logging
from app.schemas.train import TrainRequest
import pickle
from app.config import UPLOAD_DIRECTORY, MODEL_DIRECTORY, PROCESSED_DIRECTORY
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import autokeras as ak

def preprocess_data(file_name: str, input_params: list, output_params: list, scaler_type: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_name} not found.")
    
    # Load data based on file type
    if file_name.endswith(".json"):
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame.from_dict(data)
    elif file_name.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Only JSON and CSV are allowed.")
    
    # Validate columns
    missing_columns = set(input_params + output_params) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in dataset: {missing_columns}")
    
    # Extract input and output data
    input_data = df[input_params].copy()
    output_data = df[output_params].copy()
    
    # Handle missing values
    df_cleaned = pd.concat([input_data, output_data], axis=1).dropna()
    
    # Apply scaling
    if scaler_type == 'StandardScaler':
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
    elif scaler_type == 'MinMaxScaler':
        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()
    else:
        raise ValueError("Invalid scaler type. Use 'StandardScaler' or 'MinMaxScaler'.")
    
    scaled_X = scaler_X.fit_transform(df_cleaned[input_params])
    scaled_y = scaler_y.fit_transform(df_cleaned[output_params])
    
    # Convert to DataFrame for easier handling
    processed_df = pd.DataFrame(scaled_X, columns=input_params)
    processed_df[output_params] = scaled_y
    
    # Return a sample of processed data
    return processed_df.head(5).to_dict()












































# import os
# import json
# import pandas as pd
# import joblib
# from app.schemas.train import TrainRequest
# import pickle
# from fastapi import HTTPException
# from app.config import UPLOAD_DIRECTORY, MODEL_DIRECTORY
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import MinMaxScaler
# import autokeras as ak

# async def get_dataset_columns(dataset_name: str):
#     """
#     Fetch columns from a dataset file (JSON or CSV).
#     """
#     dataset_path = os.path.join(UPLOAD_DIRECTORY, dataset_name)  # Treat as file

#     if not os.path.exists(dataset_path):
#         raise HTTPException(status_code=404, detail=f"Dataset file '{dataset_name}' not found.")

#     try:
#         if dataset_name.endswith(".json"):
#             with open(dataset_path, "r") as f:
#                 data = json.load(f)
#             return {"columns": list(data[0].keys())}  # Extract keys from first JSON object
#         elif dataset_name.endswith(".csv"):
#             df = pd.read_csv(dataset_path)
#             return {"columns": df.columns.tolist()}  # Extract column names
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error reading dataset columns: {str(e)}")


# async def train_model_with_tuner(data, tuner_type):
#     """
#     Train a model with the specified tuner type using input and output params.
#     """
#     try:
#         # Load dataset (JSON or CSV)
#         # project_dir = os.path.join(UPLOAD_DIRECTORY, data.project_name)
#         data_path = os.path.join(UPLOAD_DIRECTORY, data.dataset_name) #using dataset_name directly

#         if not os.path.exists(data_path):
#             raise HTTPException(status_code=400, detail="Data file does not exist.")
        
#         with open(data_path, "r") as f:
#             data = json.load(f)

#         # Ensure input/output parameters exist in the dataset
#         missing_input_params = [param for param in data.input_params if param not in data]
#         missing_output_params = [param for param in data.output_params if param not in data]

#         if missing_input_params or missing_output_params:
#             raise HTTPException(status_code=400, detail=f"Missing parameters: {', '.join(missing_input_params + missing_output_params)}")

#         # Prepare data for training
#         input_data = pd.DataFrame({param: data[param] for param in data.input_params})
#         output_data = pd.DataFrame({param: data[param] for param in data.output_params})

#         # Split data
#         X_train, X_test, y_train, y_test = train_test_split(input_data, output_data, test_size=0.2, random_state=42)

#         # Scale data
#         scaler_X = MinMaxScaler()
#         scaler_y = MinMaxScaler()
#         X_train_scaled = scaler_X.fit_transform(X_train)
#         y_train_scaled = scaler_y.fit_transform(y_train)

#         # Train model
#         regressor = ak.StructuredDataRegressor(
#             project_name=data.project_name,
#             tuner=tuner_type,
#             max_trials=100,
#             overwrite=True,
#             loss='mean_absolute_error'
#         )
#         regressor.fit(X_train_scaled, y_train_scaled, epochs=100, validation_split=0.1)

#         # Save model and scaler
#         model_dir = os.path.join(MODEL_DIRECTORY, f"{data.project_name}_{tuner_type}")
#         os.makedirs(model_dir, exist_ok=True)
#         regressor.export_model().save(os.path.join(model_dir, "model.h5"))
#         joblib.dump(scaler_X, os.path.join(model_dir, "scaler_X.pkl"))
#         joblib.dump(scaler_y, os.path.join(model_dir, "scaler_y.pkl"))

#         # Save input and output params
#         params = {"input_params": data.input_params, "output_params": data.output_params}
#         with open(os.path.join(model_dir, "params.json"), "w") as f:
#             json.dump(params, f)

#         return {"tuner": tuner_type, "status": "success", "model_path": model_dir}

#     except Exception as e:
#         return {"tuner": tuner_type, "status": "failed", "error": str(e)}
