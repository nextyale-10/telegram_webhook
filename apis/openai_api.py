
from openai import OpenAI,AsyncOpenAI
from dotenv import load_dotenv
import os
from config.config import sessions,config
import logging
from datetime import datetime


load_dotenv(override=True)

API_KEY = os.getenv("OPENAI_KEY")
client = AsyncOpenAI(api_key=API_KEY)

async def get_response(query: str,chatId=None,useHistory=False,role="user",temperature=0,systemMessage=None):
    history  = sessions[chatId]["freeTalkHistory"]
    if systemMessage is not None:
        history.append(systemMessage)
    currentRound = {"role":role,"content":f"{query}"}
    if not useHistory:        
        tempHistory =[systemMessage,
                    currentRound] if systemMessage is not None else [currentRound]
    else:
        history.append(currentRound)

    response = await client.chat.completions.create(
            model="gpt-4o",
            messages=history if useHistory else tempHistory,
            temperature=temperature
        )
    resp_text = response.choices[0].message.content
    
    if useHistory:
        userQuery = history.pop()
        
        # pop system message to avoid side effect for other professions
        if systemMessage is not None:
            history.pop()
        history.append(userQuery)
    
    logging.info(f"get response from openai to chat {chatId if chatId else 'NOT_SPECIFIED'}: {resp_text}")
    
    return resp_text
    ...