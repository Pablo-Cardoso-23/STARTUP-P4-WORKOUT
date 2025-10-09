import locale
import re

from fastapi.params import Cookie

from app.models.chatbot import INTENTS, SENSITIVE_PATTERNS
import unicodedata
import sqlite3
from fastapi import FastAPI, Request, Form, HTTPException, Depends, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from starlette.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from passlib.hash import pbkdf2_sha256
from jose import jwt, JWTError
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
DB_PATH = "p4workout.db"
SECRET_KEY = os.getenv("SECRET_KEY", "senha123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SQLITE_DB = os.getenv("SQLITE_DB", "./startup.db")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

treinos = [
    {"id": 1, "nome": "Treino A", "exercicios": [
        {"nome": "Supino Reto", "repeticoes": 10, "series": 4},
    ]},

    {"id": 2, "nome": "Treino B", "exercicios": [
        {"nome": "Agachamento Livre", "repeticoes": 10, "series": 4},
    ]}
]

def verify_token(access_token: str = Cookie(None)) -> str:

    if not access_token:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def criar_tabelas():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS solicitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER NOT NULL,
        profissional_id INTEGER NOT NULL,
        mensagem TEXT,
        status TEXT DEFAULT 'pendente',
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profissionais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            foto TEXT,
            avaliacao REAL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profissionais_nutricao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            foto TEXT,
            avaliacao REAL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            cpf TEXT UNIQUE,
            tipo_usuario TEXT,
            area_profissional TEXT,
            cref TEXT,
            crm TEXT,
            created_at TEXT DEFAULT (CURRENT_TIMESTAMP)

        );
    """)
    conn.commit()
    conn.close()

def seed_profissionais():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profissionais")

    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO profissionais (nome, especialidade, foto, avaliacao)
            VALUES(?, ?, ?, ?)
        """, [
            ("Carlos Silva", "Musculação e Hipertrofia", "/static/img/profissionalDeMusculacao.png", 4.7),
            ("Ana Souza", "Treinamento Funcional", "/static/img/profissionalDeFuncional.png", 4.8),
            ("João Pereira", "Crossfit e Condicionamento", "/static/img/profissionalDeCondicionamento.png", 4.9)
        ])
        conn.commit()
    conn.close()

def seed_profissionais_nutricao():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profissionais_nutricao")

    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO profissionais_nutricao (nome, especialidade, foto, avaliacao)
            VALUES(?, ?, ?, ?)
        """, [
            ("Dra. Fernanda Lima", "Nutricionista Esportiva", "/static/img/profissionalDeNutricaoEsportiva.png", 4.9),
            ("Dr. Rafael Torres", "Nutrição Clínica e Performance", "/static/img/profissionalClinicaePerformance.png", 4.8),
            ("Dra. Camila Souza", "Nutrição Funcional", "/static/img/profissionalDeNutricaoFuncional.png", 4.7)
        ])
        conn.commit()
    conn.close()

init_db()
seed_profissionais()
seed_profissionais_nutricao()
criar_tabelas()


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

@app.get("/static/{path:path}")
async def server_static(path: str):
    file_path = os.path.join("app/static", path)

    if os.path.exists(file_path):
        if path.endswith(".css"):
            return FileResponse(file_path, media_type="text/css")
        return FileResponse(file_path)
    return {"erro": "Arquivo não encontrado"}

@app.get("/menu")
def exibir_menu(request: Request, user: str = Depends(verify_token)):
    dias_semana = [
        "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO", "DOMINGO"
    ]
    dia_atual = dias_semana[datetime.now().weekday()]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT nome, tipo_usuario FROM users WHERE email = ?", (user,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="USUÁRIO NÃO ENCONTRADO"
        )

    nome_usuario, tipo_usuario = row

    return templates.TemplateResponse(
        "menu.html",
        {"request": request,
         "nome_usuario": nome_usuario,
         "dia_atual": dia_atual,
         "tipo_usuario": tipo_usuario
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

@app.post("/treinos/{treino_id}/editar")
def editar_treino(treino_id: int, nome: str = Form(...)):
    for t in treinos:
        if t["id"] == treino_id:
            t["nome"] = nome
            break
    return RedirectResponse("/treinos", status_code=303)

@app.post("/treinos/{treino_id}/excluir")
def excluir_treino(treino_id: int):
    global treinos
    treinos = [t for t in treinos if t["id"] != treino_id]
    return RedirectResponse("/treinos", status_code=303)

@app.post("/treinos/{treino_id}/exercicios/adicionar")
def adicionar_exercicio(treino_id: int, nome: str = Form(...), repeticoes: int = Form(...), series: int = Form(...)):
    for t in treinos:
        if t["id"] == treino_id:
            t["exercicios"].append({"nome": nome, "repeticoes": repeticoes, "series": series})
            break

    return RedirectResponse("/treinos", status_code=303)

@app.post("/treinos/{treino_id}/exercicios/{exercicio_index}/editar")
def editar_exercicio(
        treino_id: int,
        exercicio_index: int,
        nome: str = Form(...),
        repeticoes: int = Form(...),
        series: int = Form(...)
):
    for t in treinos:
        if t["id"] == treino_id:
            if 0 <= exercicio_index < len(t["exercicios"]):
                t["exercicios"][exercicio_index] = {
                    "nome": nome,
                    "repeticoes": repeticoes,
                    "series": series
                }
    return RedirectResponse("/treinos", status_code=303)

@app.post("/treinos/{treino_id}/exercicios/{exercicio_index}/excluir")
def excluir_exercicio(treino_id: int, exercicio_index: int):
    for t in treinos:
        if t["id"] == treino_id:
            if 0 <= exercicio_index < len(t["exercicios"]):
                t["exercicios"].pop(exercicio_index)
    return RedirectResponse("/treinos", status_code=303)

@app.get("/solicitar-treino")
def solicitar_treino(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome, especialidade, foto, avaliacao FROM profissionais")
    profissionais = [
        {"id": row[0], "nome": row[1], "especialidade": row[2], "foto": row[3], "avaliacao": row[4]}
        for row in cur.fetchall()
    ]
    conn.close()

    return templates.TemplateResponse(
        "telaSolicitarTreino.html",
        {"request": request, "profissionais": profissionais}
    )

@app.post("solicitacoes/adicionar")
def adicionar_solicitacao(profissional_id: int = Form( ... ), aluno_id: int = Form(...), mensagem: str = Form("")):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO solicitacoes (profissional_id, aluno_id, mensagem) VALUES (?, ?, ?)",
                (profissional_id, aluno_id, mensagem))
    conn.commit()
    conn.close()
    return RedirectResponse("/menu", status_code=303)

@app.get("/profissional/solicitacoes")
def listar_solicitacoes(request: Request):
    #tipo = request.session.get("tipo")

    #if tipo != "profissional":

     #   return  RedirectResponse("/menu", status_code=303)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT s.id, s.aluno_id, s.mensagem, s.data
    FROM solicitacoes s
    WHERE s.status = 'pendente'
    """)
    solicitacoes = [{"id": row[0], "aluno_id": row[1], "mensagem": row[2], "data": row[3]} for row in cur.fetchall()]
    conn.close()
    return templates.TemplateResponse("telaSolicitacoes.html", {"request": request, "solicitacoes": solicitacoes})

@app.post("/enviar-solicitacao")
def enviar_solicitacao(profissinal_id: int = Form(...)):
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

dias_semana = [
        "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO", "DOMINGO"
    ]
rotinas = [
    {"id": 1, "nome": "Rotina Cutting", "alimentos": {dia: [] for dia in dias_semana}}
]

@app.get("/rotina")
def listar_rotinas(request: Request):
    return templates.TemplateResponse(
        "telaRotina.html",
        {"request": request, "rotinas": rotinas}
    )

@app.post("/rotinas/adicionar")
def adicionar_rotina(nome: str = Form( ... )):
    novo_id = max(r["id"] for r in rotinas) + 1 if rotinas else 1
    rotinas.append({"id": novo_id, "nome": nome, "alimentos": {dia: [] for dia in dias_semana}})
    return RedirectResponse("/rotina", status_code=303)

@app.post("/rotinas/{rotina_id}/excluir")
def excluir_rotina(rotina_id: int):
    global rotinas
    rotinas = [r for r in rotinas if r["id"] != rotina_id]
    return RedirectResponse("/rotina", status_code=303)

@app.post("/rotinas/{rotina_id}/adicionar-alimento/{dia}")
def adicionar_alimento(rotina_id: int, dia: str, alimento: str = Form(...)):
    for r in rotinas:
        if r["id"] == rotina_id:
            r["alimentos"][dia].append(alimento)
    return RedirectResponse("/rotina", status_code=303)

@app.post("/rotinas/{rotina_id}/adicionar_alimento/{dia}")
def adicionar_alimento(rotina_id: int, dia: str, alimento: str = Form(...)):
    for r in rotinas:
        if r["id"] == rotina_id:
            r["alimentos"][dia].append(alimento)
    return RedirectResponse("/rotina", status_code=303)

@app.post("/rotinas/{rotina_id}/editar-alimento/{dia}/{alimento_index}")
def editar_alimento(rotina_id: int, dia: str, alimento_index: int, alimento: str = Form(...)):
    for r in rotinas:
        if r["id"] == rotina_id:
            r["alimentos"][dia][alimento_index] = alimento
    return RedirectResponse("/rotina", status_code=303)

@app.post("/rotinas/{rotina_id}/excluir-alimento/{dia}/{alimento_index}")
def excluir_alimento(rotina_id: int, dia: str, alimento_index: int):
    for r in rotinas:
        if r["id"] == rotina_id:
            if 0 <= alimento_index < len(r["alimentos"][dia]):
                r["alimentos"][dia].pop(alimento_index)
    return RedirectResponse("/rotina", status_code=303)

registros = []

@app.get("/acompanhamento")
def listar_registros(request: Request):
    return templates.TemplateResponse(
        "telaAcompanhamento.html",
        {"request": request, "registros": registros}
    )

@app.post("/acompanhamento/adicionar")
def adicionar_registro(
        calorias_consumidas: int = Form(...),
        calorias_gastas: int = Form(...),
        peso: float = Form(...),
        agua: int = Form(...),
        treinos: int = Form(...)
):
    novo_id = max([r["id"] for r in registros], default=0) + 1
    registros.append({
        "id": novo_id,
        "data": datetime.today().strftime("%d/%m/%Y"),
        "calorias_consumidas": calorias_consumidas,
        "calorias_gastas": calorias_gastas,
        "peso": peso,
        "agua": agua,
        "treinos": treinos
    })
    return RedirectResponse("/acompanhamento", status_code=303)


@app.post("acompanhamento/{reg_id}/editar")
def editar_registro(
        reg_id: int,
        calorias_consumidas: int = Form(...),
        calorias_gastas: int = Form(...),
        peso: float = Form(...),
        agua: int = Form(...),
        treinos: int = Form(...)
):
    for r in registros:
        if r["id"] == reg_id:
            r.update({
                "calorias_consumidas": calorias_consumidas,
                "calorias_gastas": calorias_gastas,
                "peso": peso,
                "agua": agua,
                "treinos": treinos
            })
    return RedirectResponse("/acompanhamento", status_code=303)

@app.post("/acompanhamento/{reg_id}/excluir")
def excluir_registro(reg_id: int):
    global registros
    registros = [r for r in registros if r["id"] != reg_id]
    return RedirectResponse("/acompanhamento", status_code=303)

@app.get("/solicitar-rotina")
def solicitar_rotina_page(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome, especialidade, foto, avaliacao FROM profissionais_nutricao")
    profissionais = [
        {"id": row[0], "nome": row[1], "especialidade": row[2], "foto": row[3], "avaliacao": row[4]}
        for row in cur.fetchall()
    ]
    conn.close()
    return templates.TemplateResponse(
        "telaSolicitarRotina.html",
        {"request": request, "profissionais": profissionais}
    )

@app.post("/enviar-solicitacao-rotina")
def enviar_solicitacao_rotina(profissional_id: int = Form( ... )):
    return RedirectResponse(url="/rotina", status_code=303)

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("telaLogin.html", {"request": request})

@app.post("/login")
def login(email: str = Form( ... ), senha: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if not row or not pbkdf2_sha256.verify(senha, row[0]):
        return JSONResponse({"erro": "Credenciais inválidas"}, status_code=401)

    token = jwt.encode({"sub": email}, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse(url="/menu", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, secure=False, samesite="Strict")

    return response

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("telaCadastro.html", {"request": request})

@app.post("/register")
def register(nome: str = Form(...),
             email: str = Form( ... ),
             cpf: str = Form( ... ),
             senha: str = Form(...),
             confirmar_senha: str = Form(...),
             tipo_usuario: str = Form(...),
             area_profissional: Optional[str] = Form(None),
             cref: Optional[str] = Form(None),
             crm: Optional[str] = Form(None),
             ):

    if senha != confirmar_senha:
        return {"erro": "AS SENHAS NÃO CONFEREM"}

    if tipo_usuario == "profissional":
        if area_profissional not in ("educacao_fisica", "nutricao"):
            return {"erro": "Área profissional inválida."}
        if area_profissional == "educacao_fisica" and not cref:
            return {"erro": "CREF obrigatório"}
        if area_profissional == "nutricao" and not crm:
            return {"erro": "CRM obrigatório"}
    else:
        area_profissional = None
        cref = None
        crm = None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ? OR cpf = ?", (email, cpf))

    if cur.fetchone():
        conn.close()
        return {"erro": "E-mail ou CPF já cadastrado."}

    hashed_pw = pbkdf2_sha256.hash(senha)
    cur.execute("""
        INSERT INTO users (nome, email, password, cpf, tipo_usuario, area_profissional, cref, crm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, hashed_pw, cpf, tipo_usuario, area_profissional, cref, crm))

    conn.commit()
    conn.close()
    return {"success": True, "redirect": "/login"}
    # return RedirectResponse(url="/login", status_code=303)
