from fastapi import APIRouter, Request
from datetime import datetime
from fastapi.templating import Jinja2Templates

def get_router(templates: Jinja2Templates):
    router = APIRouter()

    @router.get('/menu')
    def exibir_menu(request: Request):
        return templates.TemplateResponse("menu.html", {"request": request})

    return router
