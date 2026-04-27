import os
import asyncio
from pyrogram import Client
from pyrogram.enums import ChatType
from dotenv import load_dotenv
import time

# Carrega as variáveis do seu .env
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Usa a sessão já criada
os.makedirs("data", exist_ok=True)
app = Client("data/meu_userbot", api_id=API_ID, api_hash=API_HASH)

async def listar_grupos():
    async with app:
        print("\n=== SEUS GRUPOS E CANAIS ===")
        # Pega as suas conversas
        async for dialog in app.get_dialogs():
            time.sleep(5)
            # Agora usando os Enums oficiais da v2.0
            if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                print(f"Nome: {dialog.chat.title}")
                print(f"ID:   {dialog.chat.id}\n")

app.run(listar_grupos())