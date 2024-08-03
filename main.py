from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from dotenv import load_dotenv
import os
load_dotenv()

DEV_FRONTEND_URL = os.getenv("DEV_FRONTEND_URL")
origins = [
    DEV_FRONTEND_URL
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
def index():
  return FileResponse("frontend/dist/index.html")
