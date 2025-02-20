from pydantic import BaseModel
from typing import Dict, List

class PredictRequest(BaseModel):
    """
    Schema for the prediction request.
    """
    project_name: str       # Name of the project to load the model from
    input_data: Dict[str, float]  # Input data for making predictions (key-value pairs)

class PredictResponse(BaseModel):
    """
    Schema for the prediction response.
    """
    prediction: List[float]  # Predicted output values