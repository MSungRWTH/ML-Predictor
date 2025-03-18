from pathlib import Path

ROOT_PATH = Path(__file__).parents[2]

UPLOAD_DIRECTORY = ROOT_PATH / "backend" / "app" / "data" / "uploads"
MODEL_DIRECTORY = ROOT_PATH / "backend" / "app" / "data" / "models"
PROCESSED_DIRECTORY = ROOT_PATH / "backend" / "app" / "data" / "processed"


for path in (UPLOAD_DIRECTORY, MODEL_DIRECTORY, PROCESSED_DIRECTORY):
    if not path.exists():
        path.mkdir(parents=True)



