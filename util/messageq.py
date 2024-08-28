import asyncio
import logging
from apis import telegram_api
from telegram.error import RetryAfter
queue = asyncio.Queue(50)

async def queueMessage(chat_id: int, text: str, bot_id: int = 0,parse_mode="Markdown"):
    await queue.put((chat_id,text,bot_id,parse_mode))
    logging.info(f"Push message to queue {queue.qsize()}/50")

async def messageSender():
    retry = False
    chat_id,text,bot_id,parse_mode = None,None,None,None
    while True:
        if not retry:
            chat_id,text,bot_id,parse_mode = await queue.get()
        try:
            await telegram_api.sendMessage(chat_id,text,bot_id,parse_mode)
            retry = False
        except RetryAfter:
            logging.warning("Limit reached, retry after 5 seconds")
            
            await asyncio.sleep(5)
            retry = True
            continue
            ...
        queue.task_done()