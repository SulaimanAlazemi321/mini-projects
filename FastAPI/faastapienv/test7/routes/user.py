from models import User
from database import localSession
from fastapi import  Depends, HTTPException, status, APIRouter, Request
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from fastapi import Cookie, Response
from fastapi.responses import JSONResponse, RedirectResponse
from .config import settings   
import httpx
import secrets
import base64
from io import BytesIO
from fastapi.responses import Response as FastAPIResponse
import re
import requests  # Add this for reCAPTCHA verification

router = APIRouter(
    tags=["User"],
    prefix="/user"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

# Google OAuth settings
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

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
            "role": "TheRole",
        }
    }}

# Add this Pydantic schema after the existing schemas
class SignupSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=6)
    recaptcha_response: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "newuser",
                "email": "user@example.com", 
                "password": "securepassword",
                "recaptcha_response": "captcha_response_here"
            }
        }
    }

# ---------Avatar Route ------------- 

@router.get("/avatar/{user_id}")
async def get_user_avatar(user_id: int, db: dbDepends):
    """Serve user avatar with caching"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    try:
        # Fetch the image from Google and serve it
        async with httpx.AsyncClient() as client:
            response = await client.get(user.avatar_url, timeout=10.0)
            if response.status_code == 200:
                return FastAPIResponse(
                    content=response.content,
                    media_type="image/jpeg",
                    headers={
                        "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                        "Access-Control-Allow-Origin": "*"
                    }
                )
    except Exception as e:
        print(f"Error fetching avatar: {e}")
    
    # If we can't get the avatar, return 404
    raise HTTPException(status_code=404, detail="Avatar not available")

# ---------Google OAuth Routes ------------- 

@router.get("/google/login")
async def google_login(response: Response):
    """Redirect to Google OAuth"""
    state = secrets.token_urlsafe(32)  # Generate random state for security
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}"
    )
    
    # Store state in cookie for verification
    response = RedirectResponse(url=google_auth_url)
    response.set_cookie(
        key="oauth_state", 
        value=state, 
        httponly=True, 
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=600  # 10 minutes
    )
    return response

@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: dbDepends,
    response: Response,
    code: str = None,
    state: str = None,
    oauth_state: str = Cookie(None)
):
    """Handle Google OAuth callback"""
    
    # Check if we have the required parameters
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    if not state:
        raise HTTPException(status_code=400, detail="State parameter not provided")
    
    # Verify state parameter for security
    if not oauth_state or oauth_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Clear the state cookie
    response.delete_cookie("oauth_state")
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Get user info from Google
            user_response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            user_info = user_response.json()
            
        # Extract user information
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        
        # Modify the picture URL to get a smaller size
        if picture:
            picture = picture.replace("s96-c", "s48-c")
        
        if not google_id or not email:
            raise HTTPException(status_code=400, detail="Required user information not available")
        
        # Check if user exists by Google ID or email
        existing_user = db.query(User).filter(
            (User.google_id == google_id) | (User.email == email)
        ).first()
        
        if existing_user:
            # Update existing user's info if needed
            if not existing_user.google_id:
                existing_user.google_id = google_id
            if not existing_user.email:
                existing_user.email = email
            if not existing_user.full_name:
                existing_user.full_name = name
            if not existing_user.avatar_url:
                existing_user.avatar_url = picture
            
            db.commit()
            user = existing_user
        else:
            # Create new user
            user = create_oauth_user(db, email, google_id, name, picture)
        
        # Create JWT token
        token = create_access_token(
            user.username, 
            user.id, 
            user.role, 
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Set cookie and redirect
        redirect_response = RedirectResponse(url="/")
        redirect_response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,  
            secure=False,  # Set to True in production
            samesite="lax", 
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return redirect_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

def create_oauth_user(db: Session, email: str, google_id: str, name: str, picture: str) -> User:
    """Create a new user from Google OAuth data"""
    new_user = User(
        username=email,
        email=email,
        google_id=google_id,
        full_name=name,
        avatar_url=picture,
        role="user",
        hashed_password=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_regular_user(db: Session, username: str, password: str, role: str) -> User:
    """Create a new user with username/password"""
    new_user = User(
        username=username,
        hashed_password=pwd_context.hash(password),
        role=role,
        email=None,
        google_id=None,
        full_name=None,
        avatar_url=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Add this after your existing user creation functions
def verify_recaptcha(recaptcha_response: str) -> bool:
    """Verify reCAPTCHA response with Google"""
    secret_key = settings.RECAPTCHA_SECRET_KEY
    
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ---------Regular Authentication Routes ------------- 

@router.post("/token")
async def login_for_access(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbDepends, response: Response):
    # Note: OAuth2PasswordRequestForm doesn't include custom fields, so we'll handle this differently
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not user.hashed_password or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  
        secure=False,  
        samesite="lax", 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message": "Login successful", "token_type": "bearer"}

# Add a new endpoint for login with reCAPTCHA
class LoginSchema(BaseModel):
    username: str
    password: str
    recaptcha_response: str

@router.post("/login")
async def login_with_captcha(login_data: LoginSchema, db: dbDepends, response: Response):
    """Login with reCAPTCHA verification"""
    
    # Verify reCAPTCHA
    if not verify_recaptcha(login_data.recaptcha_response):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA verification failed"
        )
    
    # Verify user credentials
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not user.hashed_password or not pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Create token
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  
        secure=False,  
        samesite="lax", 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message": "Login successful", "token_type": "bearer"}

def create_access_token(username: str, id: int, role: str, expire_time: timedelta):
    encode = {"sub": username, "id": id, "role": role}
    expires = int((datetime.now(timezone.utc) + expire_time).timestamp())
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(response: Response, access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")

        if not user_id or not username or not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user ")
        return {"username": username, "id": user_id, "role": role}
    except ExpiredSignatureError:
        response.delete_cookie("access_token")  
        raise HTTPException(status_code=401, detail="token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid token")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

# ---------User Management Routes ------------- 

@router.get("/get-users",  status_code=status.HTTP_200_OK)
async def get_user(db: dbDepends):
    return db.query(User).all()

@router.post("/add-user", status_code=status.HTTP_201_CREATED)
async def add_user(db: dbDepends, user_param: User_User_Schema):
    """Create a new user with username/password"""
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_param.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already exists"
        )
    
    try:
        new_user = create_regular_user(db, user_param.username, user_param.password, user_param.role)
        return {"message": f"User {new_user.username} created successfully", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
async def signup_user(signup_data: SignupSchema, db: dbDepends):
    """Create a new user account with email verification"""
    
  
    
    if not validate_email(signup_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Verify reCAPTCHA
    if not verify_recaptcha(signup_data.recaptcha_response):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA verification failed"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == signup_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == signup_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        new_user = User(
            username=signup_data.username,
            email=signup_data.email,
            hashed_password=pwd_context.hash(signup_data.password),
            role="user",
            google_id=None,
            full_name=None,
            avatar_url=None
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "Account created successfully",
            "username": new_user.username,
            "user_id": new_user.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

@router.delete("/delete-user-by-id", status_code=status.HTTP_200_OK)
async def delete_user_by_id(db: dbDepends, user_parm: User_ID_Schema):
    """Delete a user and all their reflections"""
    
    # Find the user
    user_to_delete = db.query(User).filter(User.id == user_parm.id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        # Import Reflection model here to avoid circular import
        from models import Reflection
        
        # Delete all reflections belonging to this user first
        user_reflections = db.query(Reflection).filter(Reflection.user_id == user_parm.id).all()
        for reflection in user_reflections:
            db.delete(reflection)
        
        # Now delete the user
        db.delete(user_to_delete)
        db.commit()
        
        return {"Success": f"User {user_to_delete.username} and all their reflections deleted successfully"}
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete user: {str(e)}"
        )
