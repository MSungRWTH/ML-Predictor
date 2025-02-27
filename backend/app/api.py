from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import uploadR
from app.routers import predictR, trainR

# Initializes the FastAPI app and includes all routers.

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(uploadR.router, prefix="/upload", tags=["upload"])
app.include_router(trainR.router, prefix="/train", tags=["train"])
app.include_router(predictR.router, prefix="/predict", tags=["predict"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}