from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from model.database import local_session
from typing import Annotated, Optional
from model.model import Customers
from pydantic import BaseModel, Field
from passlib.context import CryptContext 
from fastapi.templating import Jinja2Templates
from datetime import datetime
from starlette.responses import RedirectResponse




template = Jinja2Templates(directory="static/template")

template.env.globals["now"] = datetime.utcnow 

pass_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

class customer_schema(BaseModel):
    username : str = Field(min_length=3, max_length=25)
    email : str= Field(min_length=10, max_length=50) 
    password : str = Field(min_length=8, max_length=50)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "yourName",
                "email": "yourEmail",
                "password": "yourPassword",
            }
        }
    }

router = APIRouter(
    prefix="/customer",
    tags=["customer"]
)



def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]


@router.get("/get_all_customers")
async def get_customers(db: db_dependency):
    return db.query(Customers).all()


@router.get("/login")
async def login(req: Request, error: str | None = None):
    return template.TemplateResponse("login.html", {"request": req, "error": error})

@router.get("/home")    
async def home_page(request: Request):
    return template.TemplateResponse("home.html", {"request": request})




