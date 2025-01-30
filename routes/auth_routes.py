from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from fastapi.templating import Jinja2Templates

from auth import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    authenticate_user
)
from models import User
from base import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login")
async def login_form(request: Request):
    # Check if user is already logged in
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/token")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Set cookie with token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Enable for HTTPS
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    # Return JSON response for API clients
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse({"access_token": access_token, "token_type": "bearer"})
    
    # Redirect to dashboard for browser clients
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return RedirectResponse(url="/login", status_code=302)

@router.get("/profile")
async def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if "application/json" in request.headers.get("accept", ""):
        return {
            "username": current_user.username,
            "is_admin": current_user.is_admin,
            "last_login": current_user.last_login
        }
    
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "user": current_user
        }
    )

# Optional: Add a route to check authentication status
@router.get("/check-auth")
async def check_auth(current_user: User = Depends(get_current_user)):
    return {"authenticated": True, "username": current_user.username}