from pydantic import BaseModel
from typing import List

class TrainRequest(BaseModel):
    """
    Schema for the model training request.
    """
    project_name: str # Name of the project to train the model for
    dataset_name: str # Name of the dataset JSON/CSV
    input_params: List[str] # List of input feature names
    output_params: List[str] # List of output feature names
    split_type: str         # How to split the data (e.g., "train_test", "train_only")
    tuner_type: str         # Type of hyperparameter optimization (e.g., "random", "hyperband")

class TrainResponse(BaseModel):
    """
    Schema for the model training response.
    """
    message: str            # Success or error message
    project_name: str       # Name of the project where the model is saved