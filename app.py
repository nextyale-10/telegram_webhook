from fastapi import FastAPI, Request,Depends
import logging
from typing import Annotated, List

from config import config

from telegram import Update
from typing import Union
from handlers import *

app = FastAPI()

config.setup()

db_dependency = Annotated[Session, Depends(config.get_db)]

@app.post("/")
async def telegram_webhook(update: Union[dict,None],db:Session = Depends(config.get_db)):
    # j = await update.json()
    logging.info(f"Update: {update}")
    if "message" in update:
        message = update["message"]
        if "entities" in message and message["entities"][0]["type"] == "bot_command":
            logging.info(f"Command")
        else:
            await messageHandler(update["message"],db)
    ...
