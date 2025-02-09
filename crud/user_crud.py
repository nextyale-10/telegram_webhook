
from sqlalchemy.orm import Session
from do.model import User
import datetime

def check_user_exists(telegram_id: int,db:Session) -> bool:
    try:
        db_user  = db.query(User).filter(User.telegram_id == telegram_id).first()
        if db_user:
            return True
        else:
            return False
    except:
        return False
def create_user(telegram_id: int,db:Session):
    try:
        db_user = User(telegram_id=telegram_id,last_active=datetime.datetime.now())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except:
        return None
def update_user_activity_time(telegram_id: int,db:Session):
    try:
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        db_user.last_active = datetime.datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    except:
        None