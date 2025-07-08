from Models.database import engine
from Models.model import base
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from Routes import ecoUser, view
from fastapi.staticfiles import StaticFiles



app = FastAPI()
template = Jinja2Templates(directory="Views")



base.metadata.create_all(bind = engine)
app.mount("/static", StaticFiles(directory="Views"), name="static")

app.include_router(ecoUser.router)
app.include_router(view.router)

