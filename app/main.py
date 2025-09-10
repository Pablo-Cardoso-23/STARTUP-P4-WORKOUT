import locale
import re

import unicodedata

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from starlette.responses import FileResponse, RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

INTENTS = [

    {
        "name": "frequencia_treino",
        "patterns": [
            r"\bquant[oa]s?\s+dias?\s+(devo|deveria|posso)\s+treinar\b",
            r"\bfrequ[eê]ncia\s+de\s+treino\b",
            r"\btreinar\s+por\s+semana\b",
        ],

        "answer": (
            "De forma geral, 3 a 5 dias/semana funcionam bem para a maioria.\n"
            "- Iniciantes: 2–3 dias, focando em movimentos base e técnica.\n"
            "- Intermediários: 3–5 dias, distribuindo grupos musculares.\n"
            "- Avançados: 4–6 dias, com volume e recuperação bem planejados.\n"
            "Inclua 1–2 dias de descanso ativo. Ajuste conforme tempo, sono e recuperação.\n"
            "Conteúdo educativo — não substitui orientação profissional."

        )
    },

    {
        "name": "aquecimento",
        "patterns": [
            r"\bcomo\s+aquecer\b",
            r"\baquecimento\b",
            r"\bwarm[- ]?up\b"
        ],

        "answer": (
            "Aqueça por 5–10 min com cardio leve + mobilidade específica.\n"
            "Faça 1–2 séries leves do primeiro exercício antes da carga de trabalho."

        )
    },

    {
        "name": "hidratacao",
        "patterns": [
            r"\bhidrata[cç][aã]o\b",
            r"\bquanto\s+de\s+[àa]gua\b"
        ],

        "answer": (
            "Mantenha hidratação ao longo do dia. No treino, beba pequenas quantidades a cada 10–20 min.\n"
            "Necessidades variam com clima, intensidade e suor."

        )
    },
]

SENSITIVE_PATTERNS = [
    r"\b(les[aã]o|dor (aguda|forte)|medica[cç][aã]o|rem[eé]dio\b)"
]

def normalize_text(text: str) -> str:
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text.lower().strip()

def detect_intent(text: str):
    t = normalize_text(text)

    for intent in INTENTS:
        for pat in intent["patterns"]:
            if re.search(pat, t):
                return intent["name"], intent["answer"], 0.9
    return None, None, 0.0

def is_sensitive(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(p, t) for p in SENSITIVE_PATTERNS)

# (LUCAS VAI SUBSTITUIR E IMPLEMENTAR COM O BANCO DE DADOS)
treinos = [
    {"id": 1, "nome": "Treino A", "exercicios": [
        {"nome": "Supino Reto", "repeticoes": 10, "series": 4},
    ]},

    {"id": 2, "nome": "Treino B", "exercicios": [
        {"nome": "Agachamento Livre", "repeticoes": 10, "series": 4},
    ]}
]

@app.get("/static/{path:path}")
async def server_static(path: str):
    file_path = os.path.join("app/static", path)

    if os.path.exists(file_path):
        if path.endswith(".css"):
            return FileResponse(file_path, media_type="text/css")
        return FileResponse(file_path)
    return {"erro": "Arquivo não encontrado"}

@app.get("/menu")
def exibir_menu(request: Request):
    nome_usuario = "Pablo" # APRIMORAR ARA RECONHECER NO LOGIN
    dias_semana = [
        "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO", "DOMINGO"
    ]
    dia_atual = dias_semana[datetime.now().weekday()]

    return templates.TemplateResponse(
        "menu.html",
        {"request": request,
         "nome_usuario": nome_usuario,
         "dia_atual": dia_atual
         })

@app.get("/treinos")
def listar_treinos(request: Request):

    return templates.TemplateResponse(
        "telaTreino.html",
        {"request": request, "treinos": treinos}
    )

@app.post("/treinos/adicionar")
def adicionar_treino(nome: str = Form( ... )):
    novo_id = max(t["id"] for t in treinos) + 1 if treinos else 1
    treinos.append({"id": novo_id, "nome": nome, "exercicios": []})
    return RedirectResponse("/treinos", status_code=303)

@app.post("/treinos/{treino_id}/exercicios/adicionar")
def adicionar_exercicio(treino_id: int, nome: str = Form(...), repeticoes: int = Form(...), series: int = Form(...)):
    for t in treinos:
        if t["id"] == treino_id:
            t["exercicios"].append({"nome": nome, "repeticoes": repeticoes, "series": series})

        return RedirectResponse("/treinos", status_code=303)

@app.get("/chatbot")
def chatbot_page(request: Request):
    return templates.TemplateResponse(
        "chatbot.html",
        {"request": request}
    )

@app.post("/chat")
def chat(message: str = Form(...)):
    if is_sensitive(message):
        return {
            "reply": "Isso parece exigir avalização personalizada. Procure um profissional de saúde qualificado.",
            "intent": "sensível",
            "confidence": 0.8
        }

    intent, answer, confidence = detect_intent(message)

    if intent:
        return {"reply": answer, "intent": intent, "confidence": confidence}

    return {
        "reply": "Ainda não tenho uma resposta pronta para isso. Posso falar sobre: frequência de treino, aquecimento, hidratação, treino iniciante, treino avançado"
                 "nutricionista, roupa adequada, alongamento, suplementos.",
        "intent": "fallback",
        "confidence": 0.2
    }

