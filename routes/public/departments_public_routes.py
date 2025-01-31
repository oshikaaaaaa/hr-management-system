from fastapi import APIRouter, Request, Depends,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Department
from base import SessionLocal

router = APIRouter(
    prefix="/departments-public",  # Changed from departments_public to match URL conventions
    tags=["departments-public"]
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def list_public_departments(request: Request, db: Session = Depends(get_db)):
    # Query only departments (not employees as in your original code)
    departments = db.query(Department).all()
    return templates.TemplateResponse(
        "departments_public/list.html",  # Changed template path
        {"request": request, "departments": departments}
    )

@router.get("/{department_id}", response_class=HTMLResponse)
async def view_public_department(
    department_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return templates.TemplateResponse(
        "departments_public/detail.html",
        {"request": request, "department": department}
    )