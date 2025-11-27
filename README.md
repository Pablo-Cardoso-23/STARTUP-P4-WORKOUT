# P4 WORKOUT

**Disciplina:** STARTUPS

**Tema:** Design de Experiência para Apps Digitais

**Nome do Projeto:** P4 WORKOUT

**Resumo:**
P4 WORKOUT é uma aplicação web construída em Python (FastAPI) para gerenciamento de treinos, rotinas alimentares e acompanhamento de usuários. O sistema permite cadastro de usuários e profissionais, criação/edição/exclusão de treinos e exercícios, solicitação de rotinas ou treinos a profissionais, acompanhamento de métricas (peso, calorias, água) e um chatbot voltado para dúvidas frequentes sobre treino e nutrição.

**Objetivo do projeto:** Propor uma experiência digital para usuários que buscam organizar e acompanhar seus treinos e rotinas nutricionais, com foco em usabilidade e respostas rápidas via chatbot.

**Tecnologias (observadas na pasta `app/`):**
- **Linguagem:** Python
- **Framework web:** FastAPI
- **Templates:** Jinja2 (`app/templates`)
- **Banco:** SQLite (arquivo local, `DB_PATH` em `app/config.py`)
- **Autenticação:** JWT via `python-jose` e cookies
- **Outros:** `passlib` (hash de senha), `python-dotenv`, `uvicorn`, `pytz`

**Instalação e execução (rápido):**
- Criar e ativar ambiente virtual:
	- `python -m venv .venv`
	- `source .venv/Scripts/activate` (no `bash.exe` do Windows)
- Instalar dependências:
	- `pip install -r requirements.txt`
- Definir variáveis de ambiente (opcional): crie um arquivo `.env` com pelo menos:
	- `SECRET_KEY` (ex: uma chave longa aleatória)
	- `ALGORITHM=HS256`
	- `SQLITE_DB=./startup.db` (ou deixar o padrão em `app/config.py`)
- Rodar a aplicação (desenvolvimento):
	- `uvicorn app.main:app --reload --port 8000`
	- ou `python -m uvicorn app.main:app --reload --port 8000`

Observação: o arquivo `requirements.txt` atualmente está vazio — adicione as dependências necessárias antes de instalar. Recomendação mínima:
```
fastapi
uvicorn[standard]
jinja2
python-dotenv
passlib[bcrypt]
python-jose
pytz

```

**Estrutura principal (baseada na pasta `app/`):**
- `app/main.py` : entrada da aplicação (FastAPI), endpoints e lógica de rotas.
- `app/config.py` : configuração simples (ex.: `DB_PATH`).
- `app/database.py` : (se presente) utilitários de conexão com DB.
- `app/models/` : modelos e lógica de negócio (ex.: `chatbot.py`, `rotina.py`, `treino.py`, `usuario.py`).
- `app/routers/` : organização de rotas em módulos (ex.: `chat.py`, `menu.py`, `rotina.py`, `treino.py`).
- `app/schemas/` : Pydantic schemas (validação/serialização) para dados de entrada/saída.
- `app/services/` : serviços que encapsulam lógica (ex.: `chat_service.py`, `rotina_service.py`, `treino_service.py`).
- `app/templates/` : templates Jinja2 (ex.: `telaLogin.html`, `menu.html`, `telaTreino.html`, etc.).
- `app/static/` : arquivos estáticos (imagens, CSS, JS). `app/static/img/` contém imagens de profissionais e ícones.
- `uploads/` : diretório para uploads de usuário (criado automaticamente em runtime).

**Endpoints e páginas importantes (resumo):**
- `GET /` ou `GET /menu` : painel principal (requer autenticação)
- `GET /login`, `POST /login` : autenticação
- `GET /register`, `POST /register` : cadastro de usuários
- `GET /treinos`, `POST /treinos/*` : listagem e CRUD de treinos e exercícios
- `GET /rotina`, `POST /rotinas/*` : listagem e CRUD de rotinas alimentares
- `GET /acompanhamento`, `POST /acompanhamento/*` : registros de acompanhamento (peso, calorias, água)
- `GET /chatbot`, `POST /chat` : interface e backend do chatbot
- WebSocket `ws/notificacoes/{professor_id}` : notificações em tempo real para profissionais

**Configuração do banco de dados:**
- O projeto usa SQLite por padrão (`DB_PATH` em `app/config.py` aponta para `p4workout.db`). As tabelas são inicializadas automaticamente em `app/main.py` (funções `init_db()`, `criar_tabelas()` e seeds para profissionais).

**Boas práticas e próximos passos sugeridos:**
- Preencher `requirements.txt` com as dependências reais.
- Criar um `.env.example` com as variáveis de ambiente necessárias.
- Adicionar instruções de migração/backup do SQLite, se necessário.
- Escrever testes automatizados básicos para endpoints críticos (autenticação, CRUD de treinos/rotinas).

**Contribuição:**
- Abra uma issue para reportar bugs ou sugerir melhorias.
- Faça um fork e envie um Pull Request com mudanças descritas no PR.

**Contato / Autoria:**
- Projeto: `P4 WORKOUT` — disciplina STARTUPS
- Tema: Design de Experiência para Apps Digitais

---
