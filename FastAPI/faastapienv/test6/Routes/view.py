from fastapi import APIRouter, Request, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from fastapi.templating import Jinja2Templates
import Routes.ecoUser
from Models.database import local_session
from Models.model import ecoUser, ecoUsertypes, ecoCategories, ecoFacilities  # CHANGED: Added ecoFacilities and ecoCategories
from fastapi.responses import RedirectResponse
import math  



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
    



@router.get("/editFacility/{facility_id}")
async def getEditFacilityPage(req: Request, facility_id: int):
    db = local_session()
    try:
        # Get the specific facility to edit
        facility = db.query(ecoFacilities).filter(ecoFacilities.id == facility_id).first()
        
        # Get categories and users for dropdowns
        categories = db.query(ecoCategories).all()
        ecoUsers = db.query(ecoUser).all()
        
        if not facility:
            # If facility not found, redirect to home page
            return RedirectResponse(url="/", status_code=302)
            
    finally:
        db.close()
    
    return template.TemplateResponse("/Template/editFacility.html", {
        "request": req,
        "facility": facility,
        "categories": categories,
        "ecoUsers": ecoUsers
    })




@router.get("/", status_code=status.HTTP_200_OK)
async def getHomePage(req: Request, category: Optional[int] = None, contributor: Optional[int] = None, page: int = 1):
    db = local_session()
    try:
        # Pagination settings
        page_size = 10
        offset = (page - 1) * page_size
        
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

        # Get total count for pagination
        total_facilities = facilities_query.count()
        total_pages = math.ceil(total_facilities / page_size)
        
        # Get paginated facilities
        facilities = facilities_query.order_by(ecoFacilities.id).offset(offset).limit(page_size).all()
        
        # Get categories and users for dropdowns
        categories = db.query(ecoCategories).all()
        ecoUsers = db.query(ecoUser).all()

        # Smart pagination - only show 7 pages around current page
        def get_page_numbers(current, total, window=3):
            """Calculate which page numbers to show in pagination"""
            if total <= 7:
                return list(range(1, total + 1))
            
            start = max(1, current - window)
            end = min(total, current + window)
            
            # Adjust if we're near the beginning or end
            if end - start < 2 * window:
                if start == 1:
                    end = min(total, start + 2 * window)
                else:
                    start = max(1, end - 2 * window)
            
            return list(range(start, end + 1))
        
        page_numbers = get_page_numbers(page, total_pages)
        
        # Pagination info
        pagination_info = {
            "current_page": page,
            "total_pages": total_pages,
            "total_facilities": total_facilities,
            "page_size": page_size,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None,
            "page_numbers": page_numbers,
            "show_first": 1 not in page_numbers,
            "show_last": total_pages not in page_numbers,
            "show_first_ellipsis": page_numbers[0] > 2,
            "show_last_ellipsis": page_numbers[-1] < total_pages - 1
        }

    finally:
        db.close()
    
    return template.TemplateResponse("/Template/index.html", {
        "request": req, 
        "facilities": facilities, 
        "categories": categories, 
        "ecoUsers": ecoUsers,
        "pagination": pagination_info
    })