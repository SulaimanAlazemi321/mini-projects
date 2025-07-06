from sqlalchemy import Column,String,Boolean,Integer,ForeignKey
from Models.database import base

class ecoUser(base):
    __tablename__ = "ecoUser"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String)