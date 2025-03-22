from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth import verify_password, create_access_token, get_db
from models import User
from datetime import date,timedelta

# Assuming you've imported the update_last_login function
from auth import update_last_login

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
async def login(
    response: Response,
    request:Request,
    
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "auth/login.html", 
            {
                "request": request, 
                "error": "Incorrect username or password"
            }
        )

    # Update last login
    user.last_login = date.today()
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    
    # Set cookie with token
    redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    
    return redirect_response

@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response