from pydantic import BaseModel
from typing import Dict, List

class PredictRequest(BaseModel):
    model_name: str  # Add the model_name attribute
    project_name: str
    input_data: Dict[str, float]
class PredictResponse(BaseModel):
    """
    Schema for the prediction response.
    """
    prediction: List[float]  # Predicted output values