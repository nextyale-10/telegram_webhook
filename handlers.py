import logging
from fastapi import Depends

from apis.openai_api import get_response
from apis.telegram_api import *
from sqlalchemy.orm import Session
from crud.user_crud import *
from config import config

async def messageHandler(message: dict,db:Session= Depends(config.get_db)):
    logging.info(f"Message: {message}")
    chat_id = message["chat"]["id"]
    text = message["text"]
    response = get_response(text)
    
    # response = "this is a response"
    if not check_user_exists(chat_id,db):
        create_user(chat_id,db)
    else:
        update_user_activity_time(chat_id,db)
    
    await sendMessage(chat_id, response)
    
async def commandHandler(message: dict,db:Session= Depends(config.get_db)):
    ...