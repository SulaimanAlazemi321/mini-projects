from models import User
from database import localSession
from fastapi import  Depends, HTTPException, status, APIRouter
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Cookie, Response
from fastapi.responses import JSONResponse



router = APIRouter(
    tags=["User"],
    prefix="/user"
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")



def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

dbDepends = Annotated[Session, Depends(get_db)] 



# ---------Pydantic classes ------------- 

class User_ID_Schema(BaseModel):
    id: int = Field(gt=0)

    model_config={"json_schema_extra": {
        "example": {
            "id": "TheID"
        }
    }}


class Token(BaseModel):
    access_token: str 
    token_type: str 


class User_User_Schema(BaseModel):
    username: str = Field(min_length=2)
    password: str = Field(min_length=2)
    role: str = Field(min_length=2)



    model_config={"json_schema_extra": {
        "example": {
            "username": "TheUsername",
            "password": "ThePassword",
            "role": "TheRole"
        }
    }}




@router.post("/token")
async def login_for_access(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbDepends, response: Response):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user (login_for_access)")

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES))
 # Set HttpOnly cookie instead of returning token
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,  # Prevents JavaScript access
        secure=False,    # HTTPS only (set to False for development)
        samesite="lax", # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message": "Login successful", "token_type": "bearer"}



def create_access_token(username: str, id: int, role: str, expire_time: timedelta):
    encode = {"sub": username, "id": id, "role": role}
    expires = datetime.now(timezone.utc) + expire_time
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(access_token: str = Cookie(None)):
    
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user (get_current_user)")
    
    # Remove "Bearer " prefix if present
    token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        

        if not user_id or not username or not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user (get_current_user)")
        return {"username": username, "id": user_id, "role": role}
    except JWTError as e:
        print(f"DEBUG: JWT Error: {e}")  # Debug line
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user (get_current_user)")



@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

# ---------Get Users ------------- 

@router.get("/get-users",  status_code=status.HTTP_200_OK)
async def get_user(db: dbDepends):
    return db.query(User).all()


# ---------Add User ------------- 

@router.post("/add-user", status_code=status.HTTP_201_CREATED)
async def add_user(db: dbDepends, user_parm: User_User_Schema):
    new_user = User(
       
        username = user_parm.username,
        hashed_password = pwd_context.hash(user_parm.password),
        role = user_parm.role
    )
    try:
        db.add(new_user)
        db.commit()
        return {"Seccuss": "User Added"}
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@router.delete("/delete-user-by-id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(db: dbDepends, user_parm: User_ID_Schema):
    deleted_User = db.query(User).filter(User.id == user_parm.id).first()
    if not deleted_User:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        db.delete(deleted_User)
        db.commit()
        return {"Seccuss": "User Deleted"}
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
