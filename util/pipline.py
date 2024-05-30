from util.customized_ds import DotDict
from config.config import config,sessions,logging
import json
from apis import telegram_api,openai_api
import time
class Pipline:
    def __init__(self,chatId):
        
        self.chatId = chatId
        
        with open(config.script_path) as f:
            
            self.piplineDict = DotDict(json.load(f))
        self.waitingInput = False 
        self.stepId = 0
        self.messageId = 0
        self.forwarded = False
        self.end = False
    async def run(self,received = False):
        
        steps = self.piplineDict.steps
        try:
            for i in range(self.stepId,len(steps)):
                step = steps[i]
                messages = step.messages
                for j in range(self.messageId,len(messages)):
                    if self.forwarded:
                        # if last message is forwarded, then there are something stored in sessions
                        await telegram_api.sendMessage(self.chatId,step.messages[j].content.format(**sessions[self.chatId]),bot_id=messages[j].sender)
                        self.forwarded = False
                    else:
                        if not self.waitingInput:
                            await telegram_api.sendMessage(self.chatId,step.messages[j].content.format(**DotDict({"config":config})),bot_id=messages[j].sender)
                    if messages[j].action=="forward":
                        self.waitingInput = True
                    if received:
                        # already received user input
                        self.waitingInput = False
                        received = False
                    # there are 3 later actions
                    # 1. forward
                    # 2. continue
                    # 3. end
                    if messages[j].action == "continue":
                        self.messageId = j+1
                        time.sleep(1)
                        continue
                    elif messages[j].action == "forward":

                        if self.waitingInput:
                            return
                        prompt = messages[j].forward.prompt
                        resp = openai_api.get_response(prompt.format(**sessions[self.chatId]))
                        sessions[self.chatId][messages[j].forward.key] = resp
                        self.forwarded = True
                        self.messageId = j+1
                        # if(self.messageId==len(messages)):
                        #     self.stepId = i+1
                        continue
                    elif messages[j].action == "end":
                        # todo more controls in future
                        self.end = True
                        sessions[self.chatId]["freeTalk"] = True
                        return
                    else:
                        logging.error(f"unknown action type {messages[j].action}")
                        
                else:
                    self.stepId = i+1
                    self.messageId = 0
        except Exception as e:
            logging.error(f"error in pipline run: {e}")
            logging.error(f"stepId: {self.stepId}, messageId: {self.messageId}")
            
            
            
    
    