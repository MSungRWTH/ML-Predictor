import os

UPLOAD_DIRECTORY = "./app/datas/uploads/" # same as data directory

MODEL_DIRECTORY = "./app/models/"

PROCESSED_DIRECTORY = "./app/datas/processed/"


os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

os.makedirs(MODEL_DIRECTORY, exist_ok=True)

os.makedirs(PROCESSED_DIRECTORY, exist_ok=True)



