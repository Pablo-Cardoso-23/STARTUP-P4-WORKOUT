import locale

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from starlette.responses import FileResponse, RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

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
