import json
from app.models import AIRequest

def build_prompt(data: dict) -> str:
    dias_semana = {
        "monday": "segunda",
        "tuesday": "terça",
        "wednesday": "quarta",
        "thursday": "quinta",
        "friday": "sexta",
        "saturday": "sábado",
        "sunday": "domingo"
    }

    dias_treino = [f"treino-{dias_semana[d]}" for d in data["available_days"]]

    prompt = (
        "Você é um coach de fitness especializado em treinos personalizados, com base nas recomendações de Mike Israetel e Jeff Nippard. "
        "Seu objetivo é gerar treinos eficientes que atendam às necessidades e limitações do usuário.\n\n"
        f"Crie {len(dias_treino)} treinos distintos (um para cada dia disponível), com os seguintes nomes de chave: {', '.join(dias_treino)}.\n"
        "Todos os principais grupos musculares (peito, costas, ombros e pernas) devem ser treinados pelo menos uma vez por semana.\n"
        "Respeite o nível e restrições do usuário, e considere a duração máxima por treino.\n\n"
        "Informações do usuário:\n"
        f"- Idade: {data['age']}\n"
        f"- Gênero: {data['gender']}\n"
        f"- Peso: {data['weight']} kg\n"
        f"- Altura: {data['height']} m\n"
        f"- Nível de experiência: {data['experience_level']}\n"
        f"- Lesões/restrições: {data['injuries']}\n\n"
        "Logística de treino:\n"
        f"- Dias por semana: {data['days_per_week']}\n"
        f"- Dias disponíveis: {', '.join([dias_semana[d] for d in data['available_days']])}\n"
        f"- Tempo por treino: {data['time_per_workout']}\n\n"
        "Objetivos:\n"
        f"- Objetivo principal: hipertrofia\n"
        "Adaptação:\n"
        "A saída deve ser um JSON **exatamente** no seguinte formato, sem campos extras ou ausentes. Use apenas os campos mostrados:\n\n"
        "```\n"
        "{\n"
        '  "treino-segunda": {\n'
        '    "nome": "Peito, Ombro & Triceps",\n'
        '    "duracao-esperada": "60 minutos",\n'
        '    "exercicios": [\n'
        '      {\n'
        '        "nome": "Supino Reto (Barra)",\n'
        '        "sets": 4,\n'
        '        "reps": 8,\n'
        '        "descanso": "90 segundos",\n'
        '        "carga": "65 kg"\n'
        '      },\n'
        '      ...\n'
        '    ]\n'
        '  },\n'
        '  ...\n'
        "}\n"
        "```\n"
        "Importante:\n"
        "- Cada treino deve conter apenas os campos mostrados acima.\n"
        "- Nos campos de carga deve aparecer apenas xx kg. Caso seja de halteres ou algo semelhante, deve aparecer a soma dos pesos, ou seja, o peso total. Caso seja um exercício de peso corporal, deixe como 0 kg.\n"
        "- Os nomes das chaves devem seguir o padrão `treino-[dia-da-semana]`, em português.\n"
        "- Os treinos devem seguir recomendações baseadas em evidência científica de progressão, volume e recuperação muscular."
    )
    return prompt
