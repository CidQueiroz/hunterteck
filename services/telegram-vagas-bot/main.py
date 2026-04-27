"""
Userbot Telegram (Pyrogram) + Groq AI para Filtragem de Vagas.

Este script escuta canais/grupos do Telegram, realiza um pré-filtro lexical,
garante a idempotência via SQLite e envia as vagas aderentes (Score >= 80)
via Telegram Bot para o usuário.
"""
import os
import re
import json
import sqlite3
import hashlib
import asyncio
import logging
import aiohttp
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram import idle
from dotenv import load_dotenv

# ==========================================
# Configuração de Logs
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vagas_bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# Variáveis de Ambiente
# ==========================================
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MEU_USER_ID = os.getenv("MEU_USER_ID")
CHAT_IDS_STR = os.getenv("CHAT_IDS", "")

# Garantir que pasta data exista para persistência de BD e Sessão
os.makedirs("data", exist_ok=True)

try:
    # Permite IDs negativos e positivos
    CHAT_IDS = [int(x.strip()) for x in CHAT_IDS_STR.split(",") if x.strip()]
except ValueError:
    logger.error("Erro ao processar CHAT_IDS. Devem ser inteiros separados por vírgula.")
    CHAT_IDS = []

# ==========================================
# Pré-Filtro Lexical e Prompt Groq
# ==========================================
KEYWORDS = [
    # 1. Gatilhos Universais de Emprego (PT/EN/ES)
    "vaga", "vagas", "oportunidade", "hiring", "job", "recrutamento", "seleção", 
    "we are hiring", "procuramos", "contrata-se", "buscamos", "temos vaga", "open role", "position",
    "vacante", "vacantes", "oferta de empleo", "contratación", "puesto", "empleo", "búsqueda", "buscando",
    
    # 2. Modalidade e Contrato (PT/EN/ES)
    "remoto", "remote", "home office", "híbrido", "hybrid", "clt", "pj", "b2b", 
    "freelance", "contract", "usd", "dólar", "dolar", "eur", "teletrabajo", 
    
    # 3. Níveis de Senioridade (PT/EN/ES)
    "pleno", "mid", "mid-level", "pl", "sênior", "senior", "sr", "staff", "principal", "lead", "especialista",
    
    # 4. Perfil 1: Arquitetura Cloud, DevOps e IA
    "arquiteto", "architect", "arquitecto", "cloud", "aws", "gcp", "oci", "oracle", "azure", 
    "devops", "mlops", "llm", "rag", "machine learning", "inteligência artificial", "inteligencia artificial", 
    "ai", "ia", "docker", "terraform", "ci/cd",
    
    # 5. Perfil 2: Dados (Data Science, Data Eng, BI)
    "dados", "datos", "data", "cientista", "científico", "scientist", "engenheiro de dados", "ingeniero de datos", "data engineer", 
    "analista", "analyst", "business intelligence", "bi", "power bi", "powerbi", 
    "etl", "sql", "python", "big data", "pandas", "scraping", "rpa",
    
    # 6. Perfil 3: Suporte, Infra e TI Geral
    "suporte", "soporte", "support", "helpdesk", "help desk", "service desk", "infraestrutura", "infraestructura",
    "infra", "n1", "n2", "n3", "linux", "técnico de ti", "técnico de it", "tecnico", "sysadmin"
]

GROQ_SYSTEM_PROMPT = """Você é um assistente especializado em recrutamento de TI.
O usuário tem 3 perfis profissionais e aceita vagas para qualquer um deles:
Perfil 1: Arquiteto Cloud/IA Sênior (Python, RAG, OCI, GCP, AZ, AWS).
Perfil 2: Cientista/Analista de Dados (Power BI, ETL, SQL).
Perfil 3: Analista de Infraestrutura/Suporte Técnico (N1/N2, Windows, Linux).

Avalie a seguinte mensagem de vaga de emprego. O idioma pode ser Português, Inglês ou Espanhol.
Se a vaga for aderente a QUALQUER UM desses 3 perfis, dê um score alto (>= 80). Se for pouco alinhada, dê um score menor.
Se a mensagem não for uma vaga de emprego ou for de uma área não correlata, dê score 0.

Você DEVE retornar APENAS um JSON válido e estrito com a seguinte estrutura e NADA MAIS:
{
    "score": <int entre 0 e 100>,
    "resumo": "<resumo da vaga em até 150 caracteres, em português>",
    "motivo": "<motivo do score dado em até 150 caracteres, em português>"
}
"""

# ==========================================
# Classe do Banco de Dados (Idempotência)
# ==========================================
class VagasDatabase:
    """
    Gerencia a conexão e as operações no banco SQLite para garantir idempotência.
    Utiliza hash do texto para evitar processar a mesma vaga repetida.
    """
    def __init__(self, db_path="data/vagas.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    '''CREATE TABLE IF NOT EXISTS processed_messages
                       (text_hash TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)'''
                )
        except Exception as e:
            logger.error(f"Erro ao inicializar SQLite: {e}")

    def is_processed(self, text_hash: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM processed_messages WHERE text_hash = ?', (text_hash,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Erro ao ler DB: {e}")
            return False

    def mark_processed(self, text_hash: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('INSERT OR IGNORE INTO processed_messages (text_hash) VALUES (?)', (text_hash,))
        except Exception as e:
            logger.error(f"Erro ao salvar no DB: {e}")

# ==========================================
# Instâncias Globais
# ==========================================
db = VagasDatabase()
message_queue = asyncio.Queue()

# O nome "data/meu_userbot" criará o arquivo data/meu_userbot.session
app = Client(
    "data/meu_userbot",
    api_id=API_ID,
    api_hash=API_HASH
)

# ==========================================
# Funções Auxiliares
# ==========================================
def get_text_hash(text: str) -> str:
    """Gera um hash MD5 consistente para o texto limpo."""
    clean_text = re.sub(r'\s+', ' ', text).strip().lower()
    return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

def contains_keywords(text: str) -> bool:
    """Checa se o texto contém pelo menos uma keyword do pré-filtro."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

# ==========================================
# Integrações Assíncronas (Groq e Telegram)
# ==========================================
async def evaluate_with_groq(text: str) -> dict:
    """
    Chama a API do Groq para avaliar a vaga com o modelo Llama3.
    Força a saída no formato JSON.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": GROQ_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analise a vaga e retorne APENAS o JSON:\n\n{text}"}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
    except json.JSONDecodeError:
        logger.error("Groq não retornou um JSON válido.")
        return None
    except Exception as e:
        logger.error(f"Erro na API do Groq: {e}")
        return None

async def send_telegram_alert(score: int, resumo: str, motivo: str, original_text: str, link: str):
    """
    Envia um alerta formatado para o usuário usando o Bot do Telegram.
    """
    if not BOT_TOKEN or not MEU_USER_ID:
        logger.warning("BOT_TOKEN ou MEU_USER_ID não configurados. Alerta não será enviado.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Formatação com HTML
    msg = (
        f"🚨 <b>NOVA VAGA RELEVANTE (Score: {score})</b> 🚨\n\n"
        f"📝 <b>Resumo:</b> {resumo}\n"
        f"🎯 <b>Motivo:</b> {motivo}\n\n"
        f"🔗 <b>Link:</b> {link}\n\n"
        f"📄 <b>Texto Original (Trecho):</b>\n<i>{original_text[:400]}...</i>"
    )

    payload = {
        "chat_id": MEU_USER_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                response.raise_for_status()
                logger.info(f"✅ Alerta Telegram enviado! (Score {score})")
    except Exception as e:
        logger.error(f"Erro ao enviar alerta pelo Bot do Telegram: {e}")

# ==========================================
# Worker Assíncrono da Fila
# ==========================================
async def queue_worker():
    """
    Worker que consome a fila de mensagens recebidas.
    Evita gargalos e rate-limits na API do Groq.
    """
    logger.info("Worker da fila de mensagens iniciado.")
    while True:
        try:
            msg_data = await message_queue.get()
        except asyncio.CancelledError:
            break

        try:
            text = msg_data['text']
            link = msg_data['link']
            text_hash = msg_data['hash']

            logger.info(f"🔄 Processando vaga da fila: {text_hash}")

            result = await evaluate_with_groq(text)

            if result:
                score = result.get("score", 0)
                logger.info(f"✅ Vaga avaliada! Score: {score}")

                if score >= 80:
                    await send_telegram_alert(
                        score=score,
                        resumo=result.get("resumo", "N/A"),
                        motivo=result.get("motivo", "N/A"),
                        original_text=text,
                        link=link
                    )
                
                # Marca como processada se a API respondeu adequadamente
                db.mark_processed(text_hash)
            else:
                logger.warning(f"⚠️ Resposta inválida/vazia do Groq. Não foi marcada como processada.")

            # Pausa de segurança (Rate Limit)
            await asyncio.sleep(2)
            
        except asyncio.CancelledError:
            message_queue.task_done()
            break
        except Exception as e:
            logger.error(f"Erro no queue_worker: {e}")
        finally:
            message_queue.task_done()

# ==========================================
# Handler do Pyrogram (Userbot)
# ==========================================
@app.on_message(filters.chat(CHAT_IDS) & filters.text)
async def handle_new_message(client: Client, message: Message):
    """
    Disparado em novas mensagens de texto nos chats configurados.
    Executa validações rápidas (Síncronas) antes de enfileirar.
    """
    try:
        text = message.text
        if not text:
            return

        # 1. Filtro Lexical (Economia de Tokens)
        if not contains_keywords(text):
            return

        # 2. Idempotência via Banco de Dados SQLite
        text_hash = get_text_hash(text)
        if db.is_processed(text_hash):
            return
            
        # 3. Tratamento do Link da Mensagem
        chat_username = message.chat.username
        if chat_username:
            link = f"https://t.me/{chat_username}/{message.id}"
        else:
            # Para chats privados sem username
            chat_id_str = str(message.chat.id).replace("-100", "")
            link = f"https://t.me/c/{chat_id_str}/{message.id}"

        # 4. Enfileira para o worker assíncrono processar com LLM
        await message_queue.put({
            'text': text,
            'link': link,
            'hash': text_hash
        })
        logger.info(f"📥 Mensagem adicionada à fila: {link}")

    except Exception as e:
        logger.error(f"Erro ao tratar mensagem no handler: {e}")

# ==========================================
# Inicialização
# ==========================================
async def main():
    if not API_ID or not API_HASH:
        logger.error("❌ API_ID ou API_HASH ausentes no .env!")
        return

    if not CHAT_IDS:
        logger.warning("⚠️ Nenhum CHAT_IDS configurado! O bot não vai ler nenhuma mensagem.")

    worker_task = asyncio.create_task(queue_worker())

    logger.info("🚀 Iniciando Userbot Pyrogram...")
    await app.start()
    logger.info(f"✅ Userbot logado! Escutando {len(CHAT_IDS)} chats...")
    
    # Mantém o script rodando
    await idle()
    
    logger.info("Desligando...")
    await app.stop()
    worker_task.cancel()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
