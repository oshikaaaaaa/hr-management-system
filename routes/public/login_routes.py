from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
import json
from fastapi import Form


from models import Employee, Department, Position
from enums import Gender, EmploymentStatus, PositionType
from base import SessionLocal

router = APIRouter(
    prefix="/login",
    tags=["login"]
)

templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})
@router.post("/")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Add your authentication logic here
    # For example:
    if username == "admin" and password == "your-secure-password":
        # Successful login
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        # Failed login
        raise HTTPException(status_code=401, detail="Invalid credentials")