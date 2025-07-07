from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from Models.database import local_session
from typing import Annotated
from sqlalchemy.orm import Session
from Models.model import ecoUser
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta


ALGORITHM = "HS256"

SECRET_KEY = "LoveBarrnyIsRealOhhSOOGOOD"

auth_bearer = OAuth2PasswordBearer(tokenUrl="ecoUser/token")

class Token(BaseModel):

    access_token : str

    token_type : str



template = Jinja2Templates(directory="Views")

pass_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/ecoUser",
    tags=["ecoUser"]
)


def getDB():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

dbDependency = Annotated[Session, Depends(getDB)]
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from Models.database import local_session
from typing import Annotated
from sqlalchemy.orm import Session
from Models.model import ecoUser
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta


ALGORITHM = "HS256"

SECRET_KEY = "LoveBarrnyIsRealOhhSOOGOOD"

auth_bearer = OAuth2PasswordBearer(tokenUrl="ecoUser/token")

class Token(BaseModel):

    access_token : str

    token_type : str



template = Jinja2Templates(directory="Views")

pass_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/ecoUser",
    tags=["ecoUser"]
)


def getDB():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

dbDependency = Annotated[Session, Depends(getDB)]

class user_schema(BaseModel):
    username : str = Field(min_length=3 , max_length=30)
    password : str = Field(min_length=8 , max_length=50)
    role : str  = Field(min_length=3 , max_length=10)

    model_config = {
        "json_schema_extra":{
            "example":{
                "username": "username",
                "password":"password",
                "role": "user/admin"
            }
        }
    }




@router.post("/addEcoUser", status_code=status.HTTP_201_CREATED)
async def addEcoUser(db: dbDependency, user : user_schema):
    new_User = ecoUser(
        username = user.username,
        password = pass_hasher.hash(user.password),
        role = user.role
    )
    try:
        
        db.add(new_User)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")


@router.get("/getEcoUsers")
async def getEcoUsers(db: dbDependency):
    return db.query(ecoUser).all()


@router.post("/ecoUserLogin", status_code=status.HTTP_200_OK)
async def ecoUserLogin(db: dbDependency,username: str = Body(...), password: str = Body(...)):
    username = db.query(ecoUser).filter(username == ecoUser.username).first()
    if username and pass_hasher.verify(password, username.password):
        return {"seccuss": "your logged in"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "invalid username or password")
    
@router.get("/getHomePage", status_code= status.HTTP_200_OK)
async def getHomePage(req: Request):
    return template.TemplateResponse("/Template/index.html", {"request": req})



def jwtGenerate(username: str, id: int, role: str):

    expire = datetime.now(timezone.utc) + timedelta(minutes=2000)

    encode = {"sub": username, "id": id, "role": role, "expire": expire.isoformat()}

    jwt_token = jwt.encode(algorithm=ALGORITHM, key=SECRET_KEY,claims=encode)

    return jwt_token


@router.post("/token", response_model=Token)

async def get_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db: dbDependency):

    user = ecoUserLogin(form_data.username, form_data.password, db)

    if user:

     jwt_token = jwtGenerate(user.name, user.id, user.role)

     return {"access_token": jwt_token, "token_type": "Bearer"}

    elif user == False:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid credintial")



def get_current_user(token : Annotated[str, Depends(auth_bearer)]):
    try:
        jwt_token = jwt.decode(token=token, algorithms=ALGORITHM, key=SECRET_KEY)
        username = jwt_token.get("sub") 
        id = jwt_token.get("id") 
        role = jwt_token.get("role")
        if not username or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")

user_dependency = Annotated[dict, Depends(get_current_user)]


user_dependency = Annotated[dict, Depends(get_current_user)]

class user_schema(BaseModel):
    username : str = Field(min_length=3 , max_length=30)
    password : str = Field(min_length=8 , max_length=50)
    role : str  = Field(min_length=3 , max_length=10)

    model_config = {
        "json_schema_extra":{
            "example":{
                "username": "username",
                "password":"password",
                "role": "user/admin"
            }
        }
    }




@router.post("/addEcoUser", status_code=status.HTTP_201_CREATED)
async def addEcoUser(db: dbDependency, user : user_schema):
    new_User = ecoUser(
        username = user.username,
        password = pass_hasher.hash(user.password),
        role = user.role
    )
    try:
        
        db.add(new_User)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")


@router.get("/getEcoUsers")
async def getEcoUsers(db: dbDependency):
    return db.query(ecoUser).all()


@router.post("/ecoUserLogin", status_code=status.HTTP_200_OK)
async def ecoUserLogin(db: dbDependency,username: str = Body(...), password: str = Body(...)):
    username = db.query(ecoUser).filter(username == ecoUser.username).first()
    if username and pass_hasher.verify(password, username.password):
        return {"seccuss": "your logged in"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "invalid username or password")
    
@router.get("/getHomePage", status_code= status.HTTP_200_OK)
async def getHomePage(req: Request):
    return template.TemplateResponse("/Template/index.html", {"request": req})



def jwtGenerate(username: str, id: int, role: str):

    expire = datetime.now(timezone.utc) + timedelta(minutes=2000)

    encode = {"sub": username, "id": id, "role": role, "expire": expire.isoformat()}

    jwt_token = jwt.encode(algorithm=ALGORITHM, key=SECRET_KEY,claims=encode)

    return jwt_token


@router.post("/token", response_model=Token)

async def get_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db: dbDependency):

    user = ecoUserLogin(form_data.username, form_data.password, db)

    if user:

     jwt_token = jwtGenerate(user.name, user.id, user.role)

     return {"access_token": jwt_token, "token_type": "Bearer"}

    elif user == False:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid credintial")



def get_current_user(token : Annotated[str, Depends(auth_bearer)]):
    try:
        jwt_token = jwt.decode(token=token, algorithms=ALGORITHM, key=SECRET_KEY)
        username = jwt_token.get("sub") 
        id = jwt_token.get("id") 
        role = jwt_token.get("role")
        if not username or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")

user_dependency = Annotated[dict, Depends(get_current_user)]


user_dependency = Annotated[dict, Depends(get_current_user)]
