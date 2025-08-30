import locale

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from starlette.responses import FileResponse

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

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