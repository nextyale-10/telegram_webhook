from util.customized_ds import DotDict
from config.config import config,sessions,logging
import json
from apis import openai_api
from util.messageq import queueMessage
import asyncio
class Pipline:
    def __init__(self,chatId,scriptPath):
        
        self.chatId = chatId
        
        with open(scriptPath) as f:
            
            self.piplineDict = DotDict(json.load(f))
        self.waitingInput = False 
        self.stepId = 0
        self.messageId = 0
        self.end = False
        '''
        piplineKV is a dictionary that stores variables that are indicated in JSON script
        The key named lastUserMessage is reserved for every message sent by the user during the last round
        piplineKV will be initialized with the pipline
        '''
        sessions[self.chatId]["piplineKV"] = {}
        self.piplineKV = sessions[self.chatId]["piplineKV"]
        
    async def run(self):
        
        steps = self.piplineDict.steps
        try:
            for i in range(self.stepId,len(steps)):
                step = steps[i]
                messages = step.messages
                for j in range(self.messageId,len(messages)):
                    
                    # if the pipline has been waiting for user input
                    # then restart the pipline 
                    if self.waitingInput:
                        self.waitingInput = False
                        
                    # execute actions need to be done before sending the message
                    await self.executePreActions(messages[j].preActions)
                    
                    # send the message
                    await queueMessage(self.chatId,step.messages[j].content.format(**self.piplineKV,**DotDict({"config":config})),bot_id=messages[j].sender)
                    
                    # execute actions need to be done after sending the message
                    await self.executePostActions(messages[j].postActions)
                    self.messageId = j+1
                    if self.waitingInput:
                        return    
                else:
                    self.stepId = i+1
                    self.messageId = 0
        except Exception as e:
            logging.error(f"error in pipline run: {e}")
            logging.error(f"stepId: {self.stepId}, messageId: {self.messageId}")
            raise e
    async def executePreActions(self,preActions):
        for action in preActions:
            if action.type == "forward":
                prompt = action.body.prompt
                resp = await openai_api.get_response(prompt.format(**self.piplineKV),chatId = self.chatId,useHistory=False)
                if action.body.get("key",None):
                    self.piplineKV[action.body.key] = resp
        pass
    async def executePostActions(self,postActions):
        for action in postActions:
            if action.type == "continue":
                # Create a delay to make the conversation more natural
                await asyncio.sleep(1)
                return
            elif action.type == "wait":
                # wait for user input
                self.waitingInput = True
                return
            elif action.type == "end":
                self.end = True
                sessions[self.chatId]["freeTalk"] = True
                return
        pass
            
            
            
    
    