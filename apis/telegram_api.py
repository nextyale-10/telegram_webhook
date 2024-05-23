from telegram import Bot, Update
from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_API_TOKENS = os.getenv("TELEGRAM_API_TOKENS").split(",")
bots = [Bot(token=TELEGRAM_API_TOKENS[0])]

async def sendMessage(chat_id: int, text: str):
    await bots[0].sendMessage(chat_id=chat_id, text=text)