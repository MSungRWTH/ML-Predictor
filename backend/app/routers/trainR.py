import os
import json
import asyncio
from fastapi import APIRouter, HTTPException
from app.services.train_service import train_model_with_tuner, get_dataset_columns  # Add get_dataset_columns
from app.schemas.train import TrainRequest
from app.config import MODEL_DIRECTORY, UPLOAD_DIRECTORY
from fastapi.responses import JSONResponse

router = APIRouter()

# Run training for all tuners in parallel
async def run_training_for_all_tuners(data: TrainRequest):
    tuners = ["random", "hyperband", "greedy", "bayesian"]
    tasks = []

    # Create a task for each tuner
    for tuner in tuners:
        task = asyncio.create_task(train_model_with_tuner(data, tuner))
        tasks.append(task)

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    return results

@router.post("/train/")
async def train_model_route(data: TrainRequest):
    try:
        # Run training tasks for all tuners in parallel
        results = await run_training_for_all_tuners(data)

        project_name = data.project_name
        input_params = data.input_params
        output_params = data.output_params

        # Ensure model directory exists for the project
        model_dir = os.path.join(MODEL_DIRECTORY, f"{project_name}_model")
        os.makedirs(model_dir, exist_ok=True)

        # Save params.json with input and output params
        params = {
            "input_params": input_params,
            "output_params": output_params,
        }
        with open(os.path.join(model_dir, "params.json"), "w") as f:
            json.dump(params, f)

        # Return response with results from each training task
        return JSONResponse(content={"message": "Training completed for all tuners", "results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during training: {str(e)}")

@router.get("/datasets")
async def get_datasets():
    try:
        # Fetch all available datasets (CSV or JSON)
        datasets = [
            f for f in os.listdir(UPLOAD_DIRECTORY) 
            if os.path.isfile(os.path.join(UPLOAD_DIRECTORY, f)) and (f.endswith('.csv') or f.endswith('.json'))
        ]
        return JSONResponse(content={"datasets": datasets})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error reading datasets directory: {str(e)}"})

@router.get("/train/dataset-columns/{dataset_name}")
async def get_columns(dataset_name: str):
    try:
        # Fetch columns from the specified dataset (either CSV or JSON)
        columns = await get_dataset_columns(dataset_name)
        return JSONResponse(content={"columns": columns})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error fetching columns: {str(e)}"})
