from telegram import Bot, Update
from dotenv import load_dotenv
import os
import logging

load_dotenv()
TELEGRAM_API_TOKENS = os.getenv("TELEGRAM_API_TOKENS").split(",")
bots = [Bot(token=token) for token in TELEGRAM_API_TOKENS]

async def sendMessage(chat_id: int, text: str, bot_id: int = 0,parse_mode="Markdown"):
    await bots[bot_id].sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode)
    logging.info(f"send message to {chat_id} : {text}")