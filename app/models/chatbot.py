import sqlite3
from datetime import date
import re
from app.config import DB_PATH

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

    {
        "name": "alimentacaopretreino",
        "patterns": [
            r"\bo que comer antes do treino\b",
            r"\balimenta[cç][aã]o\s+pré[- ]?treino\b",
            r"\bpré[- ]?treino\b",
        ],
        "answer": (
            "Uma boa refeição pré-treino deve fornecer energia e ser de fácil digestão.\n"
            "Combine carboidratos complexos (bata-doce, aveia, pão integral) com proteína magra (frango, ovos, iogurte).\n"
            "Evite alimento muito gordurosos ou ricos em fibras imediatamente antes do treino."
        )
    },

    {
        "name": "alimentacaopostreino",
        "patterns": [
            r"\bo que comer depois do treino\b",
            r"\balimenta[cç][aã]o\s+[- ]?treino\b",
            r"bp[oó]s[- ]?treino\b"
        ],
        "answer": (
            "Após o treino, priorize proteína para a recuperação muscular (frango, peixe, ovos, whey) e carboidratos para repor energia (arroz, batata, frutas).\n"
            "O ideal é se alimentar até 1 hora após o treino."
        )
    },

    {
      "name": "marcassuplementacao",
        "patterns": [
            r"\bquais marcas de suplementa[cç][aã]o você recomenda\b",
            r"\bsuplementa[cç][aã]o\b",
            r"\bmarcas de suplementa[cç][aã]"
        ],
        "answer": (
            "No mercado há diversas marcas de suplementação, porém sempre existem aquelas que o público em geral mais recomenda"
            "aqui está uma lista de marcas que considero confiáveis: <br>"
            "<a href='https://www.gsuplementos.com.br/' target='_blank'>GROWTH - SITE OFICIAL</a><br>"
            "<a href='https://www.maxtitanium.com.br/?utm_source=googleads&utm_medium=cpc&utm_campaign=GO_SEAR_INST_F_BR_Institucional"
            "-Impressao&utm_term=Institucional&utm_content=max%20titanium&sol_source=google&sol_content=718735163679&sol_campaign=21054127855&gad_source"
            "=1&gad_campaignid=21054127855&gbraid=0AAAAADhRO4MSp0_AvyEHgYBnx70rW3tWA&gclid=CjwKCAjw6P3GBhBVEiwAJPjmLiiEAcizVov34zxi3BO2keFZ4vCGZWRSc5Wk3B2FcwrxqMB3Obe6vRoCmX4QAvD_BwE' "
            "target='_blank'>MAX TITANIUM - SITE OFICIAL</a><br>"
            "<a href='https://www.integralmedica.com.br/todos-os-produtos?gad_source=1&gad_campaignid=22396590402&gbraid=0AAAAADoo4REwQ0XkMuSKx_4vBQo04bg9w&gclid=CjwKCAjw6P3GBhBVEiwAJPjmLkB5gL2LwjMpfhbOJCPizH1V2S2y0IbF54vE_CoBcRIKjg1zw3mf5BoC5TsQAvD_BwE"
            "' target='_blank'>INTEGRALMEDICA - SITE OFICIAL</a><br>"
            "<a href='https://darklabsuplementos.com.br/?utm_source=google&utm_medium=cpc&utm_campaign=8dh-gads-vendas-institucional&gad_source=1&gad_campaignid=19643348789&gbraid=0AAAAApDtcy55Zv4Wx2gH2iVYEXFliR3ar&gclid=CjwKCAjw6P3GBhBVEiwAJPjmLnvqwJlyL0-GSi5L-KMPcO9hVdkmrUl4js0LLxlqx1h6DtSFCfDHLRoCH_4QAvD_BwE'"
            " target='_blank'>DARK LAB - SITE OFICIAL</a><br>"
            "<a href='https://www.blackskullusa.com.br/?gad_source=1&gad_campaignid=16527934236&gbraid=0AAAAADh6h6Q8BLw_3DGzlYTAEjvLlQSly&gclid=CjwKCAjw6P3GBhBVEiwAJPjmLgxO7q-xBimUPDoNn8LtzEcIFbht00nNxtEPLwi9jC4MQgklw1Nq7hoCvJUQAvD_BwE'"
            " target='_blank'>BLACK SKULL - SITE OFICIAL</a><br>"
        )
    },

    {
        "name": "listar_treinos",
        "patterns": [
            r"\b(quais|meus)\s+treinos\b",
            r"\blistar\s+treinos\b"
        ],
        "answer": None
    },

    {
        "name": "listar_exercicios",
        "patterns": [
            r"\bexerc[ií]cios\s+do\s+(treino\s+\w+)\b",
            r"\bmostrar\s+(treino\s+\w+)\b"
        ],
        "answer": None
    }
]

SENSITIVE_PATTERNS = [
    r"\b(les[aã]o|dor (aguda|forte)|medica[cç][aã]o|rem[eé]dio\b)"
]

DB_PATH = "p4workout.db"

def process_message(message: str, user_email: str):
    for intent in INTENTS:
        for pattern in intent["patterns"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if intent["name"] == "listar_treinos":
                    return get_treinos(user_email)
                if intent["name"] == "listar_exercicios":
                    treino_nome = match.group(1)  # captura o nome do treino
                    return get_exercicios_do_treino(user_email, treino_nome)
                return intent["answer"]
    return "Não entendi sua pergunta. Pode reformular?"


def get_treinos(user_email: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM treinos WHERE usuario_email = ?", (user_email,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "Você ainda não cadastrou treinos."
    return "Seus treinos: " + ", ".join([r[1] for r in rows])

def get_exercicios_do_treino(user_email: str, treino_nome: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM treinos
        WHERE usuario_email = ? AND nome = ?
    """, (user_email, treino_nome))

    treino = cur.fetchone()

    if not treino:
        conn.close()
        return f"Não encontrei nenhum treino chamado '{treino_nome}'."

    treino_id = treino[0]

    cur.execute("""
        SELECT nome, series, repeticoes
        FROM exercicios
        WHERE treino_id = ?
    """, (treino_id,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return f"O treino '{treino_nome}' não possui exercícios cadastrados."

    resposta = f"<h4>Exercícios do {treino_nome}: </h4><ul>"

    for nome, series, reps in rows:
        resposta += f"<li>{nome} - {series} séries - {reps} repetições</li>"

    resposta += "</ul>"
    return resposta

