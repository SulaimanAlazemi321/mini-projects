from fastapi import APIRouter, Request, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from fastapi.templating import Jinja2Templates
import Routes.ecoUser
from Models.database import local_session
from Models.model import ecoUser, ecoUsertypes, ecoCategories, ecoFacilities  # CHANGED: Added ecoFacilities and ecoCategories
from fastapi.responses import RedirectResponse



router = APIRouter()
template = Jinja2Templates(directory="Views")


    
@router.get("/Login")
async def getAddUserPage(req: Request):
    db = local_session()
    try:
        categories = db.query(ecoCategories).all()
        ecoUsers = db.query(ecoUser).all()
    finally:
        db.close()
    
    return template.TemplateResponse("/Template/login.html", {
        "request": req,
        "categories": categories,
        "ecoUsers": ecoUsers
    })
    
@router.get("/addFacility")
async def getAddUserPage(req: Request):
    db = local_session()
    try:
        categories = db.query(ecoCategories).all()
        ecoUsers = db.query(ecoUser).all()
    finally:
        db.close()
    
    return template.TemplateResponse("/Template/add-facility.html", {
        "request": req,
        "categories": categories,
        "ecoUsers": ecoUsers
    })
    


@router.get("/", status_code=status.HTTP_200_OK)
async def getHomePage(req: Request, category: Optional[int] = None, contributor: Optional[int] = None):
    db = local_session()
    try:
        # Base query
        facilities_query = db.query(
            ecoFacilities, ecoCategories.name, ecoUser.username
        ).join(
            ecoCategories, ecoFacilities.category == ecoCategories.id
        ).join(
            ecoUser, ecoFacilities.contributor == ecoUser.id
        )

        # Apply filters if provided
        if category:
            facilities_query = facilities_query.filter(ecoFacilities.category == category)

        if contributor:
            facilities_query = facilities_query.filter(ecoFacilities.contributor == contributor)

        # Get all data
        facilities = facilities_query.order_by(ecoFacilities.id).all()
        categories = db.query(ecoCategories).all()
        ecoUsers = db.query(ecoUser).all()

    finally:
        db.close()
    
    return template.TemplateResponse("/Template/index.html", {
        "request": req, 
        "facilities": facilities, 
        "categories": categories, 
        "ecoUsers": ecoUsers
    })


