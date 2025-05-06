from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import os

# Carrega .env
load_dotenv()

from app.models import AIRequest
from app.services.openai_client import generate_workouts as ai_generate

app = FastAPI(title="Hyper App AI Service")

@app.post("/generate-workouts")
async def generate_workouts(request: AIRequest):
    try:
        result = ai_generate(request)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))