
from openai import OpenAI,AsyncOpenAI
from dotenv import load_dotenv
import os
from config.config import sessions,config
import logging

load_dotenv(override=True)

API_KEY = os.getenv("OPENAI_KEY")
client = AsyncOpenAI(api_key=API_KEY)

async def get_response(query: str,chatId=None,useHistory=False):
    history  = sessions[chatId]["freeTalkHistory"]
    currentRound = {"role":"user","content":f"{query}"}
    history.append(currentRound)
    if not useHistory:
        defaultConfig = config.openai.chatgpt.mode.default.starting_msg
        
        history =[{"role":defaultConfig.role,"content":defaultConfig.content},
                    currentRound]
    
    response = await client.chat.completions.create(
            model="gpt-4o",
            messages=history
        )
    resp_text = response.choices[0].message.content
    
    logging.info(f"get response from openai to chat {chatId if chatId else 'NOT_SPECIFIED'}: {resp_text}")
    
    return resp_text
    ...