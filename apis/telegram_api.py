from telegram import Bot, Update
from dotenv import load_dotenv
import os
import logging

load_dotenv(override=True)
TELEGRAM_API_TOKENS = os.getenv("TELEGRAM_API_TOKENS").split(",")
bots = [Bot(token=token) for token in TELEGRAM_API_TOKENS]

async def sendMessage(chat_id: int, text: str, bot_id: int = 0,parse_mode="Markdown"):
    logging.info(f"sending message to {chat_id} : {text}")
    await bots[bot_id].sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode)
