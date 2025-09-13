from models import Reflection, base, Question
from database import engine, localSession
from fastapi import  Depends, HTTPException, status, APIRouter, Request, Cookie
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import random
from .user import get_current_user
from jose import jwt, JWTError

router = APIRouter(
    tags=["view"],
)

template = Jinja2Templates(directory="View/template")

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

dbDepends = Annotated[Session, Depends(get_db)]

# Create optional user dependency
async def get_current_user_optional(access_token: str = Cookie(None)):
    """Returns user data if logged in, None if not logged in"""
    if not access_token:
        return None
    
    try:
        # Use the same logic as your get_current_user but don't raise exceptions
        token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token
        
        # Import these from your user.py file
        from .user import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role") or "user"

        if not user_id or not username:
            return None
        return {"username": username, "id": user_id, "role": role}
    except (JWTError, Exception):
        return None

optionalUserDepends = Annotated[Optional[dict], Depends(get_current_user_optional)]

@router.get("/")
async def index(req: Request, db: dbDepends, user: optionalUserDepends):
    questions = db.query(Question).all()
    question_text = random.choice(questions).question if questions else "What's on your mind today?"
    
    # Only get reflections if user is logged in
    if user:
        reflection = db.query(Reflection).filter(Reflection.user_id == user.get("id")).order_by(Reflection.title.desc()).all()
    else:
        reflection = None
    
    return template.TemplateResponse("index.html", {
        "request": req, 
        "ref": reflection, 
        "question": question_text,
        "user": user  # Pass user data to template
    })

@router.get("/login")
async def login_page(req: Request):
    return template.TemplateResponse("login.html", {"request": req})