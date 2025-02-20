import os

UPLOAD_DIRECTORY = "./app/datas/" # same as data directory

#MODEL_DIRECTORY = "./app/models/"
MODEL_DIRECTORY = os.path.join(os.getcwd(), "./app/models/")


os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

os.makedirs(MODEL_DIRECTORY, exist_ok=True)




