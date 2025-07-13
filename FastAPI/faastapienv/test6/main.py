from Models.database import engine
from Models.model import base
from fastapi import FastAPI
from Routes import ecoUser, view
from fastapi.staticfiles import StaticFiles

app = FastAPI()

base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="Views"), name="static")

app.include_router(ecoUser.router)
app.include_router(view.router)

