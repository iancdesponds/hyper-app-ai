from fastapi import Depends, FastAPI, HTTPException, Request
from requests import Session
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import os
from database import get_db

# Carrega .env
load_dotenv()

from app.models import Condition, PersonalInfo, TrainingAvailability, User
from app.services.openai_client import generate_workouts as ai_generate

app = FastAPI(title="Hyper App AI Service")

@app.get("/")
def read_root():
    return {"message": "Ai microservice is up!"}

@app.post("/generate-workouts")
async def generate_workouts(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    user_id = body.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user_infos = db.query(PersonalInfo).filter(PersonalInfo.id == user.id_infos).first()
    user_dates = db.query(TrainingAvailability).filter(TrainingAvailability.id == user.id_dates).first()
    user_conditions = db.query(Condition).filter(Condition.id == user.id_conditions).first()

    if not user_infos or not user_dates or not user_conditions:
        raise HTTPException(status_code=400, detail="Informações incompletas do usuário")

    try:
        # Construir o dicionário para o prompt
        input_data = {
            "first_name": user.first_name,
            "age": calculate_age(user.birth_date),
            "gender": user_infos.bio_gender,
            "weight": user_infos.weight_kg,
            "height": user_infos.height_cm / 100,
            "experience_level": "iniciante",  # Ajuste conforme sua regra
            "injuries": extract_injuries(user_conditions),
            "days_per_week": sum([getattr(user_dates, d) for d in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]),
            "available_days": [d for d in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] if getattr(user_dates, d)],
            "time_per_workout": "60 minutos"  # Pode ser ajustado conforme preferências
        }

        result = ai_generate(input_data)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_age(birth_date):
    from datetime import datetime
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def extract_injuries(condition_obj):
    # Traduz os campos com valor 1 como uma lista de lesões
    conditions_map = {
        "chronic_back_pain": "dor crônica nas costas",
        "damaged_left_upper_body": "lesão no braço esquerdo",
        "damaged_right_upper_body": "lesão no braço direito",
        "damaged_left_lower_body": "lesão na perna esquerda",
        "damaged_right_lower_body": "lesão na perna direita",
        "damaged_body_core": "lesão no core",
        "recent_surgery": "cirurgia recente",
        "pregnancy": "gravidez"
    }
    return ', '.join(desc for field, desc in conditions_map.items() if getattr(condition_obj, field) == 1) or "nenhuma"
