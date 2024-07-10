from fastapi import FastAPI, Request,Depends
import logging
from typing import Annotated, List

from config.config import config,setup,get_db,sessions

from telegram import Update
from typing import Union
from handlers import *

app = FastAPI()

setup()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/")
async def telegram_webhook(update: Union[dict,None],db:Session = Depends(get_db)):
    # j = await update.json()
    logging.info(f"Update: {update}")
    if "message" in update:
        message = update["message"]
        chat = message["chat"]
        chat_id = chat["id"]
        if not chat_id in sessions:
            sessions[chat_id] = {"freeTalk":True,"messageIds":set()}
            
            # setting up chat history with chatgpt if it is the first time.
            freetalkConfig = config.openai.chatgpt.mode.free_talk.starting_msg
            starting_message = {"role":freetalkConfig.role,"content":freetalkConfig.content}
            sessions[chat_id]["freeTalkHistory"] = [starting_message]
            
        if message["message_id"] in sessions[chat_id]["messageIds"]:
            # idempotent
            return
        else:
            sessions[chat_id]["messageIds"].add(message["message_id"])
        
        if not check_user_exists(chat_id,db):
            # todo it is actually chat not user. change the schema later
            create_user(chat_id,db)
        else:
            update_user_activity_time(chat_id,db)
            
        if "text" not in message:
            # ignore this kind of message
            logging.info(f"ignore this message : {message}")
            
            return 
        
        if "entities" in message and message["entities"][0]["type"] == "bot_command":
            logging.info(f"This is a Command : {message}")
            await commandHandler(update["message"],db)
            
        else:
            await messageHandler(update["message"],db)
    ...
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.uvicorn.host, port=config.uvicorn.port)