from fastapi import APIRouter, Request, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.templating import Jinja2Templates
import Routes.ecoUser
from Models.database import local_session
from Models.model import ecoUser

router = APIRouter()
template = Jinja2Templates(directory="Views")



@router.get("/", status_code=status.HTTP_200_OK)
async def getHomePage(req: Request):
    db = local_session()
    try:
        users = db.query(ecoUser).all()
    finally:
        db.close()
    return template.TemplateResponse("/Template/index.html", {"request": req, "users": users})
