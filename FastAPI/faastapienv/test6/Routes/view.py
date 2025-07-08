from fastapi import APIRouter, Request, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.templating import Jinja2Templates
import Routes.ecoUser
from Models.database import local_session
from Models.model import ecoUser, ecoUsertypes, ecoCategories, ecoFacilities  # CHANGED: Added ecoFacilities and ecoCategories

router = APIRouter()
template = Jinja2Templates(directory="Views")



@router.get("/", status_code=status.HTTP_200_OK)
async def getHomePage(req: Request):
    db = local_session()
    try:
        # CHANGED: Join ecoFacilities with ecoCategories and ecoUser to get facility info with category names and contributor names
        facilities =db.query(
            ecoFacilities,ecoCategories.name,ecoUser.username
        ).join(
            ecoCategories, ecoFacilities.category == ecoCategories.id
        ).join(
            ecoUser, ecoFacilities.contributor == ecoUser.id
        ).all()
    finally:
        db.close()
    return template.TemplateResponse("/Template/index.html", {"request": req, "facilities": facilities})
