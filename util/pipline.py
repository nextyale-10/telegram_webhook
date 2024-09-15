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
            while self.stepId<len(steps):
                step = steps[self.stepId]
                messages = step.messages
                while self.messageId<len(messages):
                    
                    # if the pipline has been waiting for user input
                    # then restart the pipline 
                    if self.waitingInput:
                        self.waitingInput = False
                        
                    # execute actions need to be done before sending the message
                    status = await self.executePreActions(messages[self.messageId].preActions)
                    if status==1:
                        # wait another input
                        self.waitingInput = True
                        return
                    # send the message
                    await queueMessage(self.chatId,step.messages[self.messageId].content.format(**self.piplineKV,**DotDict({"config":config})),bot_id=messages[self.messageId].sender)
                    
                    # execute actions need to be done after sending the message
                    await self.executePostActions(messages[self.messageId].postActions)
                    self.messageId += 1
                    if self.waitingInput:
                        return    
                else:
                    self.stepId += 1
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
                if "check" in action:
                    checkResp = await openai_api.get_response(action.check.prompt.format(**self.piplineKV),chatId = self.chatId,useHistory=False,temperature=0)
                    if checkResp=="1":
                        # check passed
                        return 0
                        
                    else:
                        # check failed
                        exceptionActionType = action.check.exceptionAction.type 
                        if exceptionActionType=="repeat":
                            await queueMessage(self.chatId,action.check.exceptionAction.body.content.format(**self.piplineKV))
                            return 1
        return 0
                        
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
            
            
            
    
    