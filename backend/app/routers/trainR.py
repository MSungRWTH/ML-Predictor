import os
import json
import asyncio
from typing import List
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from app.services.train_service import preprocess_data
from app.schemas.train import DatasetColumnsRequest, PreprocessRequest, PreprocessResponse, TrainRequest
from app.schemas.train import TrainRequest
from app.config import MODEL_DIRECTORY, UPLOAD_DIRECTORY, PROCESSED_DIRECTORY
from fastapi.responses import JSONResponse


router = APIRouter()

@router.get("/datasets", response_model=List[str])
def list_datasets():
    """Fetch available datasets from the upload directory."""
    try:
        files = [f for f in os.listdir(UPLOAD_DIRECTORY) if f.endswith(('.json', '.csv'))]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dataset-columns")
def get_dataset_columns(request: DatasetColumnsRequest):
    """Fetch column names from a selected dataset."""
    file_path = os.path.join(UPLOAD_DIRECTORY, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if request.filename.endswith('.json'):
            with open(file_path, 'r') as file:
                data = json.load(file)
            columns = list(data.keys())
        else:
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preprocess", response_model=PreprocessResponse)
def preprocess(request: PreprocessRequest):
    """Run preprocessing on the selected dataset."""
    file_path = os.path.join(UPLOAD_DIRECTORY, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        processed_data = preprocess_data(file_path, request.input_params, request.output_params, request.scaler_type)
        return processed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
