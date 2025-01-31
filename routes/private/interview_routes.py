
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from datetime import date, time



from models import Interview
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"]
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
async def list_interviews(request: Request, db: Session = Depends(get_db)):
    interviews = db.query(Interview).all()
    return templates.TemplateResponse(
        "interviews/list.html",
        {"request": request, "interviews": interviews}
    )

@router.post("/create")
async def create_interview(
    request: Request,
    applicant_id: int = Form(...),
    interview_date: date = Form(...),
    interview_time: time = Form(...),
    interviewed_by: int = Form(...),
    db: Session = Depends(get_db)
):
    interview = Interview(
        applicant_id=applicant_id,
        interview_date=interview_date,
        interview_time=interview_time,
        interview_status="Pending",
        interviewed_by=interviewed_by
    )
    db.add(interview)
    db.commit()
    return RedirectResponse(url="/interviews", status_code=303)