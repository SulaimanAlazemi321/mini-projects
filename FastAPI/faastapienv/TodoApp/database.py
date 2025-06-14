from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLalchemy_DataBase_URL = 'sqlite:///./todos.db'

engine = create_engine(SQLalchemy_DataBase_URL, connect_args={'check_same_thread':False})

localSession = sessionmaker(autoflush=False, autocommit = False, bind=engine)

Base = declarative_base()

