from database import base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Reflection(base):
    __tablename__ = "Reflection"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    date = Column(String)  
    reflection = Column(String)
    user_id = Column(Integer, ForeignKey("User.id"))
    user = relationship("User", back_populates="reflections")
    
class Question(base):
    __tablename__ = "Question"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)


class User(base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String) 
    role = Column(String) 
    reflections = relationship("Reflection", back_populates="user")



  

