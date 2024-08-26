
from openai import OpenAI,AsyncOpenAI
from dotenv import load_dotenv
import os
from config.config import sessions,config
import logging
from datetime import datetime


load_dotenv(override=True)

API_KEY = os.getenv("OPENAI_KEY")
client = AsyncOpenAI(api_key=API_KEY)

async def get_response(query: str,chatId=None,useHistory=False,useMemory=True):
    history  = sessions[chatId]["freeTalkHistory"]
    memoryPrompt = {"role":"system","content": f"Current Time:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}Please answer user's query based on following memory or information: {sessions[chatId]['memory']}"}
    if useMemory:
        history.append(memoryPrompt)
    currentRound = {"role":"user","content":f"{query}"}
    if not useHistory:
        defaultConfig = config.openai.chatgpt.mode.default.starting_msg
        
        tempHistory =[{"role":defaultConfig.role,"content":defaultConfig.content},
                    currentRound]
    else:
        history.append(currentRound)

    response = await client.chat.completions.create(
            model="gpt-4o",
            messages=history if useHistory else tempHistory,
            temperature=0
        )
    resp_text = response.choices[0].message.content
    
    logging.info(f"get response from openai to chat {chatId if chatId else 'NOT_SPECIFIED'}: {resp_text}")
    
    return resp_text
    ...