from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime


Base = declarative_base()


# 定义 User 类
class User(Base):
    __tablename__ = 'users'  # 定义表名
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True)
    last_active = Column(DateTime,default=datetime.datetime.now())
