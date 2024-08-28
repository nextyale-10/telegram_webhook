import logging
from fastapi import Depends

from apis.openai_api import get_response
from util.messageq import queueMessage
from sqlalchemy.orm import Session
from crud.user_crud import *
from config.config import config,get_db,sessions
from util.pipline import Pipline
import json
from datetime import datetime
import re
number = 0

MEMORY_STORE_FREQUENCY = 5

MEMORY_PROMPT = """
Based on the provided chat history in JSON format and the current time: {time}, please follow the steps below:

1. **Summarize the conversation** - Focus only on the essential points and avoid any unnecessary details.
2. **Extract important memory** - Identify and extract only the crucial information that needs to be remembered. The extracted memory should:
    - Be saved in plain text format.
    - Include time information when relevant. Convert all relative time expressions (e.g., currently={time}, today={time}, tomorrow={time}+1day, yesterday={time}-1day) into exact times or dates relative to the provided current time {time}.
    - Avoid any redundant or irrelevant details.
    - Be listed as separate memory items within a single list.
Chat history: {history}
Return the memory in the following format:

```plaintext
memory: []
"""
async def messageHandler(message: dict,db:Session= Depends(get_db)):
    global number
    if config.cur_bot!=config.host:
        # only the host do the coordination
        return
    
    logging.info(f"Message: {message}")
    if "text" not in message:
        logging.error(f"no text field in message, something wrong")
        return
    
    chatId = message["chat"]["id"]

    if sessions[chatId]["freeTalk"]:
        text = message["text"]
        # response = f"{number}. this is a test response not costing money"
        
        bots = [config.bots[botId] for botId in config.bots]
        mentionedBots = [bot for bot in bots if f"@{bot.username}" in text]
        if mentionedBots:
            """
            If user explicitly mentions a bot, then only the bot should respond to the user's query.
            
            """
            bots = mentionedBots
            
        for bot in bots:
            content = \
            f"""
            Current time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Please answer user's query based on the memory provided and your profession.
            
            Memory: {sessions[chatId]['memory']}
            
            Your profession: {bot.system_prompt}
            
            Rules: 
            1.You need to try your best to adhere your profession.
            2.You need to answer the user's query based on the memory provided if possible.
            """
            systemPrompt = {"role":"system","content":content}
            response = await get_response(text,chatId=chatId,useHistory=True,systemMessage=systemPrompt)
            await queueMessage(chatId, response,bot_id=bot.index)
            history = sessions[chatId]["freeTalkHistory"]
            history.append({"role":"assistant","content":f"[{bot.name}'s response]: {response}"})

            
        '''
        Store memory every MEMORY_STORE_FREQUENCY
        '''
        userMessageCount = _countUserMessage(sessions[chatId]["freeTalkHistory"])
        if userMessageCount!=0 and userMessageCount%MEMORY_STORE_FREQUENCY==0:
            try:
                time =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                retMem = await get_response(MEMORY_PROMPT.format(history=json.dumps(sessions[chatId]["freeTalkHistory"]),time=time),chatId=chatId,useHistory=False)
                pattern =r'\[\s*(.*?)\s*\]'
                match = re.search(pattern, retMem, re.DOTALL)

                if match:
                    memory = match.group(0)
                memory = json.loads(memory)
                for m in memory:
                    sessions[chatId]["memory"].append(m)
            except Exception as e:
                logging.error(f"error in memory format: {retMem} with error {e}")
        number+=1
    else:
        # in a pipline
        ppl = sessions[chatId]["pipline"]
        if not ppl:
            logging.error(f"no pipline in session")
            return
        sessions[chatId]["piplineKV"]["lastUserMessage"] = message["text"]
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
    
    chatId = message["chat"]["id"]
    
    if cmd=="start":
        # start the conversation
        sessions[chatId]["freeTalk"] = False
        ppl =Pipline(chatId,config.script_paths.before_bedtime)
        sessions[chatId]["pipline"]=ppl
        await ppl.run()
        if ppl.end:
            sessions[chatId]["freeTalk"] = True
            return
        ...
    
    elif cmd=="clean":
        # clean the chat history
        freetalkConfig = config.openai.chatgpt.mode.free_talk.starting_msg
        starting_message = {"role":freetalkConfig.role,"content":freetalkConfig.content}
        sessions[chatId]["freeTalkHistory"] = [starting_message]
        await queueMessage(chatId,"Chat history cleaned.")
        ...
    elif cmd=="memory":
        retval = "meomry:\n"
        
        for i,m in enumerate(sessions[chatId]["memory"]):
            retval+=f"{i}: {m}\n"
        await queueMessage(chatId,retval)
    elif cmd=="intro":
        # start an introduction session
        sessions[chatId]["freeTalk"] = False
        ppl =Pipline(chatId,config.script_paths.introduction)
        sessions[chatId]["pipline"]=ppl
        await ppl.run()
        if ppl.end:
            sessions[chatId]["freeTalk"] = True
            return
    ...
def _parseCommand(cmd: str):
    return cmd[1:].split("@")[0]
def _countUserMessage(history:list):
    return len([msg for msg in history if msg["role"]=="user"])