from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from models import User
from base import SessionLocal

# Security config
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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
    return user

# Login endpoint
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

# async def auth_middleware(request: Request, call_next):
#     # Add "/" to excluded paths
#     excluded_paths = {"/", "/login", "/token", "/static", "/docs", "/openapi.json", "/login-modal"}
#     if request.url.path in excluded_paths or request.url.path.startswith("/static/"):
#         response = await call_next(request)
#         return response

#     try:
#         token = request.cookies.get("access_token")
#         if not token:
#             return RedirectResponse(url="/login")
        
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             return RedirectResponse(url="/login")
            
#     except JWTError:
#         return RedirectResponse(url="/login")

#     response = await call_next(request)
#     return response

async def auth_middleware(request: Request, call_next):
    # Define all public paths
    public_paths = {
        "/",  # Root/public dashboard
        "/login",
        "/token",
        "/static",
        "/docs", 
        "/openapi.json",
        "/login-modal",
        "/employee-public",  # Public employee page
        "/departments-public",  # Public departments page
        "/vacancies-public",  # Public vacancies page
        # Add any other public paths here
    }
    
    # Check if path starts with any of these prefixes
    public_prefixes = {
        "/static/",
        "/public/",  # For any paths under /public/
        # Add other prefixes that should be public
    }
    
    # Check if current path is public
    is_public = (
        request.url.path in public_paths or 
        any(request.url.path.startswith(prefix) for prefix in public_prefixes)
    )
    
    if is_public:
        response = await call_next(request)
        return response

    # Authentication check for secure paths
    try:
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/login")
            
    except JWTError:
        return RedirectResponse(url="/login")

    response = await call_next(request)
    return response

def check_permission(required_role: str = None):
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if required_role and current_user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to perform this action"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator