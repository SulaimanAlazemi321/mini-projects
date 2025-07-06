from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated

from Models.database import local_session
from Models.model import ecoUser

# ───────── constants
ALGORITHM    = "HS256"
SECRET_KEY   = "LoveBarrnyIsRealOhhSOOGOOD"
ACCESS_MIN   = 60          # token life‑time

# ───────── helpers
pwd_ctx       = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="ecoUser/token")

def _db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

dbDepandency = Annotated[Session, Depends(_db)]

def _hash(pwd: str) -> str:
     return pwd_ctx.hash(pwd)
def _verify(p, h)   -> bool: 
              return pwd_ctx.verify(p, h)

def _jwt(data: dict, mins: int = ACCESS_MIN):
    data = data.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=mins)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def _auth(db: Session, u: str, p: str):
    user = db.query(ecoUser).filter(ecoUser.username == u).first()
    if user and _verify(p, user.password):
        return user
    else:
         None

# ───────── Pydantic
class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=50)
    role:     str = Field(min_length=3, max_length=10)

class Me(BaseModel):
    username: str
    role: str

# ───────── router
router = APIRouter(prefix="/ecoUser", tags=["ecoUser"])

@router.post("/addEcoUser", status_code=204)
def add_user(user: UserIn, db: dbDepandency):
    db.add(ecoUser(username=user.username, password=_hash(user.password), role=user.role))
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "DB error")

@router.post("/token", status_code=200)
def login(res: Response, db: dbDepandency,
          form: OAuth2PasswordRequestForm = Depends(),
          ):
    user = _auth(db, form.username, form.password)
    if not user:
        raise HTTPException(401, "invalid credentials")

    token = _jwt({"sub": user.username, "role": user.role})
    # ——— secure cookie —
    res.set_cookie(
        key        ="access_token",
        value      =token,
        httponly   =True,
        secure     =True,
        samesite   ="lax",
        max_age    =ACCESS_MIN*60,
        path       ="/"
    )
    return {"msg": "ok"}          # body is optional; cookie is what matters

@router.post("/logout", status_code=204)
def logout(res: Response):
    res.delete_cookie("access_token", path="/")

def _current(token: str = Depends(oauth2_scheme)):  # reads cookie automatically
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "invalid token")

@router.get("/me", response_model=Me)
def me(payload: dict = Depends(_current)):
    return {"username": payload["sub"], "role": payload["role"]}
