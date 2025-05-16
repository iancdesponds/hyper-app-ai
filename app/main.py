from datetime import datetime
import json
import traceback
from fastapi import Depends, FastAPI, HTTPException, Request
from requests import Session
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from database import get_db

# Carrega .env
load_dotenv()

from app.models import (
    Condition,
    Exercise,
    PersonalInfo,
    Series,
    Train,
    TrainingAvailability,
    User,
)
from app.services.openai_client import generate_workouts as ai_generate

app = FastAPI(title="Hyper App AI Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


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
    user_dates = (
        db.query(TrainingAvailability)
        .filter(TrainingAvailability.id == user.id_dates)
        .first()
    )
    user_conditions = (
        db.query(Condition).filter(Condition.id == user.id_conditions).first()
    )

    if not user_infos or not user_dates or not user_conditions:
        raise HTTPException(
            status_code=400, detail="Informações incompletas do usuário"
        )

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
            "days_per_week": sum(
                [
                    getattr(user_dates, d)
                    for d in [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ]
                ]
            ),
            "available_days": [
                d
                for d in [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
                if getattr(user_dates, d)
            ],
            "time_per_workout": "60 minutos",  # Pode ser ajustado conforme preferências
        }

        result = ai_generate(input_data)

        # # Salva o valor de result em um arquivo json local
        # with open("result.json", "w") as f:
        #     json.dump(result, f, indent=4)

        # Salva o resultado no banco de dados
        save_workout_to_db(db, user_id, result)

        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def save_workout_to_db(db, user_id, workout_data):
    try:
        # Converte o JSON em um dicionário
        for treino in workout_data:
            # Cria um novo treino
            try:
                expected_duration_str = workout_data[treino].get("duracao-esperada", "")
                new_train = Train(
                    id_user=user_id,
                    name=workout_data[treino]["nome"],
                    # Pega a data atual
                    date=datetime.today().date(),
                    # Pega apenas os digitos do tempo esperado
                    # Ex: "60 minutos" -> 60
                    # Ex: "120 minutos" -> 120
                    expected_duration=int(
                        "".join(filter(str.isdigit, expected_duration_str or "0"))
                    ),
                    start_time=None,  # Horário pode ser ajustado conforme necessário
                    end_time=None,  # Horário pode ser ajustado conforme necessário
                    feedback=None,  # Feedback pode ser ajustado conforme necessário
                )
                db.add(new_train)
                db.commit()
                db.refresh(new_train)
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Erro ao salvar o treino: {str(e)}"
                )

            # Adiciona os exercícios do treino
            for exercise in workout_data[treino]["exercicios"]:
                # Checa se o exercício já existe no banco
                existing_exercise = (
                    db.query(Exercise).filter(Exercise.name == exercise["nome"]).first()
                )

                if not existing_exercise:
                    # Se não existe, cria um novo
                    new_exercise = Exercise(name=exercise["nome"])
                    db.add(new_exercise)
                    db.commit()
                    db.refresh(new_exercise)
                else:
                    new_exercise = existing_exercise

                for i in range(exercise["sets"]):
                    # Cria uma nova série para cada set
                    new_series = Series(
                        id_train=new_train.id,
                        id_exercise=new_exercise.id,
                        weight=int("".join(filter(str.isdigit, exercise["carga"]))),
                        repetitions=int(
                            str("".join(filter(str.isdigit, str(exercise["reps"]))))
                        ),
                        rest_time=int(
                            "".join(filter(str.isdigit, exercise["descanso"]))
                        ),
                    )

                    db.add(new_series)
                    db.commit()
                    db.refresh(new_series)
        db.close()
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar o treino no banco de dados: {str(e)}",
        )


def calculate_age(birth_date):
    from datetime import datetime

    today = datetime.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


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
        "pregnancy": "gravidez",
    }
    return (
        ", ".join(
            desc
            for field, desc in conditions_map.items()
            if getattr(condition_obj, field) == 1
        )
        or "nenhuma"
    )
