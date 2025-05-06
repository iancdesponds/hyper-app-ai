import json
from app.models import AIRequest

def build_prompt(data: AIRequest) -> str:
    pp = data.physical_profile
    lg = data.logistics
    ob = data.objectives
    ad = data.adaptation

    prompt = (
        "Você é um coach de fitness especializado em treinos personalizados. "
        "Gere 3 treinos distintos (workout-1, workout-2, workout-3) no formato JSON abaixo, "
        "baseados nas informações do usuário:\n\n"
        "Informações do usuário:\n"
        f"- Idade: {pp.age}\n"
        f"- Gênero: {pp.gender}\n"
        f"- Peso: {pp.weight} kg\n"
        f"- Altura: {pp.height} m\n"
        f"- Nível de experiência: {pp.experience_level}\n"
        f"- Lesões/restrições: {pp.injuries or 'nenhuma'}\n\n"
        "Logística de treino:\n"
        f"- Dias por semana: {lg.days_per_week}\n"
        f"- Tempo por treino: {lg.time_per_workout}\n\n"
        "Objetivos:\n"
        f"- Objetivo principal: {ob.primary_goal}\n"
        f"- Grupos musculares prioritários: {', '.join(ob.prioritized_muscle_groups)}\n\n"
        "Adaptação:\n"
        f"- Histórico de progressão: {json.dumps(ad.progress_history) if ad.progress_history else 'nenhum'}\n"
        f"- Feedback pré-treino: {ad.pre_workout_feedback or 'nenhum'}\n"
        f"- Feedback pós-treino: {ad.post_workout_feedback or 'nenhum'}\n\n"
        "Exemplo de saída desejada (JSON):\n"
        "```\n"
        "{\n"
        '  "workout-1": { /* ... conforme exemplo fornecido */ },\n'
        '  "workout-2": { /* ... */ },\n'
        '  "workout-3": { /* ... */ }\n'
        "}\n"
        "```\n"
        "Garanta que o JSON seja válido e retrate sets, tempos e exercícios."
    )
    return prompt