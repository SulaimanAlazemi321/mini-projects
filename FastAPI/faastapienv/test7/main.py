from models import Reflection, base
from database import engine, localSession
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes import reflection, view, user
from fastapi.staticfiles import StaticFiles



base.metadata.create_all(bind=engine)


app = FastAPI()

app.mount("/static", StaticFiles(directory="View/static"), name="static")

app.include_router(reflection.router)
app.include_router(view.router)
app.include_router(user.router)


