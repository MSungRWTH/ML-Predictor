from pydantic import BaseModel
from typing import List, Optional


class TrainRequest(BaseModel):
    project_name: str
    tuner: Optional[str] = "random"  # Default value is 'random', can be 'random', 'hyperband', 'greedy', 'bayesian', or 'all'
class TrainResponse(BaseModel):
    project_name: str