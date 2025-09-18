from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from Models.database import local_session
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from Models.model import ecoUser, ecoCategories, ecoFacilities, ecoFacilityStatus, ecoUsertypes
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_




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
    userType : Optional[int] = Field(default=1)  # CHANGED: role -> userType (int)

    model_config = {
        "json_schema_extra":{
            "example":{
                "username": "username",
                "password":"password",
                "userType": 1  # CHANGED: role -> userType (int)
            }
        }
    }



class Search_schema(BaseModel):
    query : str = Field(min_length=1 , max_length=30)

class Login_schema(BaseModel):
    username : str = Field(min_length=1 , max_length=30)
    password : str = Field(min_length=8 , max_length=50)


class deleteFacility_schema(BaseModel):
    id: int

@router.post("/deleteUser")
async def deleteUser(facility: deleteFacility_schema, db: dbDependency):
    deletedUser = db.query(ecoFacilities).filter(ecoFacilities.id == facility.id).first()
    db.delete(deletedUser)
    db.commit()



class UpdateFacility_schema(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=30)
    category: int = Field(gt=0)
    description: str = Field(min_length=1, max_length=100)
    houseNumber: str = Field(min_length=1, max_length=30)
    streetName: str = Field(min_length=1, max_length=30)
    county: str = Field(min_length=1, max_length=30)
    town: str = Field(min_length=1, max_length=30)
    postcode: str = Field(min_length=1, max_length=30)
    lng: float 
    lat: float

@router.post("/updateFacility")
async def updateFacility(facility: UpdateFacility_schema, db: dbDependency):
    try:
        # Find the existing facility
        existing_facility = db.query(ecoFacilities).filter(ecoFacilities.id == facility.id).first()
        
        if not existing_facility:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found")
        
        # Update the facility fields
        existing_facility.title = facility.title
        existing_facility.category = facility.category
        existing_facility.description = facility.description
        existing_facility.houseNumber = facility.houseNumber
        existing_facility.streetName = facility.streetName
        existing_facility.county = facility.county
        existing_facility.town = facility.town
        existing_facility.postcode = facility.postcode
        existing_facility.lng = facility.lng
        existing_facility.lat = facility.lat
        
        db.commit()
        return {"detail": "Facility updated successfully"}
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.post("/liveSearch")
async def liveSearch(db: dbDependency, theQuery : Search_schema):  
    ecoFacility =  db.query(ecoFacilities, ecoCategories.name, ecoUser.username).join(
        ecoUser, ecoFacilities.contributor == ecoUser.id).join(
            ecoCategories, ecoFacilities.category == ecoCategories.id
        ).filter(
            or_(ecoUser.username.like(f"%{theQuery.query}%"),
                ecoFacilities.title.like(f"%{theQuery.query}%"),
                ecoCategories.name.like(f"%{theQuery.query}%")
                )
                ).limit(5).all()
    result = []
    for facility_data in ecoFacility:
        ecoFacilityObject = facility_data[0]
        categoryName = facility_data[1]
        contributorName = facility_data[2]        

        result.append({
            "ecoTitle" : ecoFacilityObject.title,
            "ecoDescription": ecoFacilityObject.description,
            "categoryName": categoryName,
            "contributorName": contributorName
        })

    return result

@router.post("/addEcoUser", status_code=status.HTTP_201_CREATED)
async def addEcoUser(db: dbDependency, user : user_schema):
    new_User = ecoUser(
        username = user.username,
        password = pass_hasher.hash(user.password),
        userType = user.userType  # CHANGED: role -> userType
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
async def ecoUserLogin(db: dbDependency,user: user_schema):
    username = db.query(ecoUser).filter(user.username == ecoUser.username).first()
    if username and pass_hasher.verify(user.password, username.password):
        return {"success": "Logged in successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid username or password")
    
@router.get("/getHomePage", status_code= status.HTTP_200_OK)
async def getHomePage(req: Request):
    return template.TemplateResponse("/Template/index.html", {"request": req})



def jwtGenerate(username: str, id: int, userType: int):  # CHANGED: role -> userType (int)

    expire = datetime.now(timezone.utc) + timedelta(minutes=2000)

    encode = {"sub": username, "id": id, "userType": userType, "expire": expire.isoformat()}  # CHANGED: role -> userType

    jwt_token = jwt.encode(algorithm=ALGORITHM, key=SECRET_KEY,claims=encode)

    return jwt_token


@router.post("/token", response_model=Token)

async def get_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db: dbDependency):

    user = ecoUserLogin(form_data.username, form_data.password, db)

    if user:

     jwt_token = jwtGenerate(user.name, user.id, user.userType)  # CHANGED: role -> userType

     return {"access_token": jwt_token, "token_type": "Bearer"}

    elif user == False:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid credintial")



def get_current_user(token : Annotated[str, Depends(auth_bearer)]):
    try:
        jwt_token = jwt.decode(token=token, algorithms=ALGORITHM, key=SECRET_KEY)
        username = jwt_token.get("sub") 
        id = jwt_token.get("id") 
        userType = jwt_token.get("userType")  # CHANGED: role -> userType
        if not username or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")
        return {"username": username, "id": id, "userType": userType}  # CHANGED: role -> userType
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid jwt")

user_dependency = Annotated[dict, Depends(get_current_user)]




class EcoFacility_schema(BaseModel):

    title: str = Field(min_length=1 , max_length=30)
    category: int = Field(  gt=0)
    description: str = Field(min_length=1,  max_length=100)
    houseNumber: str = Field(min_length=1,  max_length=30)
    streetName: str = Field(min_length=1 , max_length=30)
    county: str =Field(min_length=1 , max_length=30)
    town: str = Field(min_length=1 , max_length=30)
    postcode: str = Field(min_length=1 , max_length=30)
    lng: float 
    lat: float
    



@router.post("/addEcoFacility", status_code=status.HTTP_201_CREATED)
async def addEcoFacility(ecoFac: EcoFacility_schema, db: dbDependency):
    # Sanitize all text inputs to prevent XSS attacks
  

    
    newFacility = ecoFacilities(
        title = ecoFac.title,
        category = ecoFac.category,
        description = ecoFac.description,
        houseNumber = ecoFac.houseNumber,
        streetName = ecoFac.streetName,
        county = ecoFac.county,
        town = ecoFac.town,
        postcode = ecoFac.postcode,
        lng = ecoFac.lng,
        lat = ecoFac.lat,
        contributor = 2
    )

    try:
        
        db.add(newFacility)
        db.commit()
        return {"detail": "Facility created successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")



@router.get("/getEcoFacility")
async def getEcoFacility(db: dbDependency):
    return db.query(ecoFacilities).all()
