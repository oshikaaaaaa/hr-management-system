from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
import json

from models import Employee, Department, Position
from enums import Gender, EmploymentStatus, PositionType
from base import SessionLocal

router = APIRouter(
    prefix="/contact",
    tags=["contact"]
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
    return templates.TemplateResponse("shared/contact.html", {"request": request})