# AI Service - Hyper App

Microsserviço FastAPI que gera treinos personalizados a partir de dados do usuário usando a API do Azure OpenAI (GPT-4o).

---

## 🚀 Como configurar o projeto

### 1. Clone o repositório
```bash
git clone https://github.com/iancdesponds/hyper-app-ai.git
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/macOS
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente

Copie o arquivo .env.example para .env e preencha com seus dados:

```bash
cp .env.example .env
```

### 5. Rode o servidor localmente

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a interface Swagger para testar:

```bash
http://localhost:8000/docs
```

## 🔁 Como testar

### Endpoint disponível:

```bash
POST /generate-workouts
```

### JSON de exemplo:

```json
{
  "physical_profile": {
    "age": 28,
    "gender": "male",
    "weight": 80,
    "height": 1.78,
    "experience_level": "intermediate",
    "injuries": null
  },
  "logistics": {
    "days_per_week": 3,
    "time_per_workout": "60min"
  },
  "objectives": {
    "primary_goal": "hypertrophy",
    "prioritized_muscle_groups": ["Chest", "Back"]
  },
  "adaptation": {
    "progress_history": {
      "Bench Press": [50, 55, 60]
    },
    "pre_workout_feedback": "recovered",
    "post_workout_feedback": "medium"
  }
}
```

Clique em "Try it out" no Swagger ou envie via Postman/curl para testar a resposta da IA.

## 🧠 Observação técnica

Este microsserviço faz uso da API GPT da Azure para gerar treinos com base em perfil, disponibilidade e feedbacks do usuário. A saída é um JSON estruturado com treinos separados por grupo muscular e dia da semana.