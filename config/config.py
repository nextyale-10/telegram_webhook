import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import threading
import time
import asyncio
from crud.user_crud import *

from do.model import User
import datetime
from apis import telegram_api
from dotenv import load_dotenv
from util.customized_ds import DotDict
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
GREETING_MSG="Long time no see! How are you doing?"


def logging_config():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s -%(message)s',
                        filename='app.log',
                        filemode='a')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def set_recurring_greeting_timer(interval:int, # interval for searching db
                                 timedelta: datetime.timedelta):
    
    async def greeting(chat_id:int):
        await telegram_api.sendMessage(chat_id,GREETING_MSG)
        ...
    def run(timedelta: datetime.timedelta):
        # print("Running")
        db = SessionLocal()
        
        users = db.query(User).filter(User.last_active<(datetime.datetime.now()-timedelta)).all()

        count = 0 # limit the number of messages sent in a second
        for user in users:
            
            #todo need to write better code for this
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(greeting(user.telegram_id))
            
            # asyncio.run(greeting(user.telegram_id)) 
            update_user_activity_time(user.telegram_id,db)
            if count>25:
                count = 0
                time.sleep(1)
                
            count+=1
            
        threading.Timer(interval, run,(timedelta,)).start()
        db.close()
        
        
    threading.Timer(interval, run,(timedelta,)).start()

    ...
def setup():
    logging_config()
    set_recurring_greeting_timer(interval=5,timedelta=datetime.timedelta(seconds=60*60))
    
def read_config():
    import yaml
    with open('config.yaml', 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

config = DotDict(read_config())
sessions = DotDict(dict())
total = DotDict({"config":config,"sessions":sessions})