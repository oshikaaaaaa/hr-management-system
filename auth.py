from datetime import datetime, date,timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from base import SessionLocal


# Security constants
SECRET_KEY = "your-secret-key-here"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
def update_last_login(user, db):
    """
    Update last_login if it's None or older than 1 hour
    Works with both datetime and date objects
    """
    current_datetime = datetime.utcnow().date()
    
    # If last_login is None, update it
    if user.last_login is None:
        user.last_login = current_datetime
        db.commit()
        return
    
    # Convert last_login to date if it's a datetime
    last_login_date = user.last_login
    if isinstance(last_login_date, datetime):
        last_login_date = last_login_date.date()
    
    # Check if last login is older than 1 day
    if (current_datetime - last_login_date).days >= 1:
        user.last_login = current_datetime
        db.commit()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    
    # Update last_login timestamp
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # Update last login if needed
    current_date = date.today()
    if user.last_login is None or user.last_login < current_date:
        user.last_login = current_date
        db.commit()
    
    return user



# auth.py
async def auth_middleware(request, call_next):
    # Define public and private paths
    public_paths = {"/login", "/", "/about", "/contact", 
                   "/department_list", "/interview_dates", 
                   "/job_listing", "/position_list", "/logout"}
    
    path = request.url.path.rstrip('/')
    
    #root path
    if path == "" or path == "/":
        response = await call_next(request)
        return response
    
    # Allow static files
    if path.startswith("/static"):
        response = await call_next(request)
        return response
    
    # Better public path checking that handles subpaths
    is_public = False
    for public_path in public_paths:
        # Check if the path exactly matches or is a subpath of a public path
        if path == public_path or path.startswith(public_path + "/"):
            is_public = True
            break
    
    if not is_public:
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(
                url="/login?next=" + request.url.path,
                status_code=status.HTTP_303_SEE_OTHER
            )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if not username:
                return RedirectResponse(
                    url="/login",
                    status_code=status.HTTP_303_SEE_OTHER
                )
            
            # Add user to request state
            request.state.user = username
            
        except JWTError:
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
    
    response = await call_next(request)
    return response