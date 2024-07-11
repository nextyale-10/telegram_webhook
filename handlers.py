import logging
from fastapi import Depends

from apis.openai_api import get_response
from util.messageq import queueMessage
from sqlalchemy.orm import Session
from crud.user_crud import *
from config.config import config,get_db,sessions
from util.pipline import Pipline
number = 0
async def messageHandler(message: dict,db:Session= Depends(get_db)):
    global number
    if config.cur_bot!=config.host:
        # only the host do the coordination
        return
    
    logging.info(f"Message: {message}")
    if "text" not in message:
        logging.error(f"no text field in message, something wrong")
        return
    
    chat_id = message["chat"]["id"]
    
    if sessions[chat_id]["freeTalk"]:
        text = message["text"]
        response = await get_response(text,chatId=chat_id,useHistory=True)
        # response = f"{number}. this is a test response not costing money"
        number+=1
        await queueMessage(chat_id, response)
    else:
        # in a pipline
        ppl = sessions[chat_id]["pipline"]
        if not ppl:
            logging.error(f"no pipline in session")
            return
        if ppl.end:
            sessions[chat_id]["freeTalk"] = True
            return
        if ppl.waitingInput:
            sessions[chat_id]["input"]=message["text"]
            await ppl.run(received=True)
        else:
            # possibly ignore?
            await ppl.run()
        ...
        
        
    

    
    
    
async def commandHandler(message: dict,db:Session= Depends(get_db)):
    if config.cur_bot!=config.host:
        # only the host do the coordination
        return
    
    if "text" not in message:
        logging.error(f"no text field in message, something wrong")
        return
    
    cmd = _parseCommand(message["text"])
    
    chat_id = message["chat"]["id"]
    
    if cmd=="start":
        # start the conversation
        sessions[chat_id]["freeTalk"] = False
        ppl =Pipline(chat_id)
        sessions[chat_id]["pipline"]=ppl
        await ppl.run()
        if ppl.end:
            sessions[chat_id]["freeTalk"] = True
            return
        ...
    
    elif cmd=="clean":
        # clean the chat history
        freetalkConfig = config.openai.chatgpt.mode.free_talk.starting_msg
        starting_message = {"role":freetalkConfig.role,"content":freetalkConfig.content}
        sessions[chat_id]["freeTalkHistory"] = [starting_message]
        await queueMessage(chat_id,"Chat history cleaned.")
        ...
    ...
def _parseCommand(cmd: str):
    return cmd[1:].split("@")[0]