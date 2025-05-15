import os
import json
import requests
from fastapi import HTTPException
from app.models import AIRequest
from app.utils import build_prompt

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key  = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not endpoint or not api_key:
    raise RuntimeError("Variáveis de ambiente da OpenAI não configuradas")


def generate_workouts(data: dict) -> dict:
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2025-01-01-preview"
    headers = {"Content-Type": "application/json", "api-key": api_key}

    messages = [
        {"role": "system", "content": "Você é um assistente que gera planos de treino."},
        {"role": "user", "content": build_prompt(data)}
    ]
    body = {"messages": messages, "max_tokens": 2000, "temperature": 0.7}

    resp = requests.post(url, headers=headers, json=body)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    content = resp.json()["choices"][0]["message"]["content"]
    print("Resposta bruta da IA:\n", content)

    try:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_data = content[json_start:json_end].strip()
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"Resposta da IA não era JSON válido. Erro: {str(e)}")
