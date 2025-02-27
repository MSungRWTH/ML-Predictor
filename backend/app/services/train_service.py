from fastapi import HTTPException
import os
import json
import asyncio
from app.schemas.train import TrainRequest
from app.services.automl import AutoMLRegressor
from app.config import PROCESSED_DIRECTORY
import logging




