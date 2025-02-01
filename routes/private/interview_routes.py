
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session,joinedload
from datetime import date
from datetime import date, time
import datetime

from enums import InterviewStatus


from models import Interview,User,Applicant
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
    # Query interviews with explicit joins
    interviews = (
        db.query(Interview)
        .options(
            joinedload(Interview.applicant),
            joinedload(Interview.interviewer)
        )
        .join(User, Interview.interviewed_by == User.user_id, isouter=True)
        .join(Applicant, Interview.applicant_id == Applicant.applicant_id, isouter=True)
        .order_by(Interview.interview_date.desc(), Interview.interview_time.desc())
        .all()
    )
    
    # Add some debug logging
    print(f"Found {len(interviews)} interviews")
    
    formatted_interviews = []
    for interview in interviews:
        # Debug print
        print(f"Interview ID: {interview.interview_id}")
        print(f"Applicant ID: {interview.applicant_id}")
        print(f"Interviewer ID: {interview.interviewed_by}")
        print(f"Applicant: {interview.applicant}")
        print(f"Interviewer: {interview.interviewer}")
        
        formatted_interviews.append({
            'interview_id': interview.interview_id,
            'applicant': {
                'name': interview.applicant.full_name if interview.applicant else 'N/A',
                'id': interview.applicant_id
            },
            'interview_date': interview.interview_date.strftime('%Y-%m-%d') if interview.interview_date else 'N/A',
            'interview_time': interview.interview_time.strftime('%H:%M') if interview.interview_time else 'N/A',
            'interview_status': interview.interview_status,
            'interviewer': {
                'name': interview.interviewer.username if interview.interviewer else 'Not Assigned',
                'id': interview.interviewed_by
            },
            'interview_notes': interview.interview_notes or ''
        })

    return templates.TemplateResponse(
        "interviews/list.html",
        {
            "request": request, 
            "interviews": formatted_interviews
        }
    )

@router.get("/create", response_class=HTMLResponse)
async def create_interview_form(request: Request, db: Session = Depends(get_db)):
    # Get all applicants
    applicants = db.query(Applicant).all()
    
    # Get all users who can be interviewers
    users = db.query(User).all()
    
    return templates.TemplateResponse(
        "interviews/create.html",
        {
            "request": request,
            "applicants": applicants,
            "users": users,
            "interview_statuses": InterviewStatus
        }
    )

@router.post("/create")
async def create_interview(
    request: Request,
    applicant_id: int = Form(...),
    interview_date: str = Form(...),
    interview_time: str = Form(...),
    interview_status: InterviewStatus = Form(...),
    interviewed_by: int = Form(...),
    interview_notes: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Convert string dates and times to proper Python objects
        parsed_date = datetime.strptime(interview_date, '%Y-%m-%d').date()
        parsed_time = datetime.strptime(interview_time, '%H:%M').time()
        
        # Create new interview
        interview = Interview(
            applicant_id=applicant_id,
            interview_date=parsed_date,
            interview_time=parsed_time,
            interview_status=interview_status,
            interviewed_by=interviewed_by,
            interview_notes=interview_notes if interview_notes else None
        )
        
        db.add(interview)
        db.commit()
        
        return RedirectResponse(url="/interviews", status_code=303)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating interview: {str(e)}")
        return templates.TemplateResponse(
            "interviews/create.html",
            {
                "request": request,
                "error": "Failed to create interview. Please try again.",
                "applicants": db.query(Applicant).all(),
                "users": db.query(User).all(),
                "interview_statuses": InterviewStatus
            },
            status_code=400
        )

@router.post("/{interview_id}/delete")
async def delete_position(interview_id: int, db: Session = Depends(get_db)):
    id = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if id is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(id)
    db.commit()
    return RedirectResponse(url="/interviews", status_code=303)


# @router.get("/{employee_id}/edit", response_class=HTMLResponse)
# async def edit_employee_form(request: Request, employee_id: int, db: Session = Depends(get_db)):
#     employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
#     if employee is None:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return templates.TemplateResponse(
#         "employees/edit.html",
#         {"request": request, "employee": employee}
#     )

# @router.post("/{employee_id}/edit")
# async def edit_employee(
#     request: Request,
#     employee_id: int,
#     first_name: str = Form(...),
#     last_name: str = Form(...),
#     date_of_birth: date = Form(...),
#     gender: Gender = Form(...),
#     hire_date: date = Form(...),
#     department_id: int = Form(...),
#     position_id: int = Form(...),
#     position_type: PositionType = Form(...),
#     salary: float = Form(...),
#     employment_status: EmploymentStatus = Form(...),
#     db: Session = Depends(get_db)
# ):
#     employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
#     if employee is None:
#         raise HTTPException(status_code=404, detail="Employee not found")
        
#     employee.first_name = first_name
#     employee.last_name = last_name
#     employee.date_of_birth = date_of_birth
#     employee.gender = gender
#     employee.hire_date = hire_date
#     employee.department_id = department_id
#     employee.position_id = position_id
#     employee.position_type = position_type
#     employee.salary = salary
#     employee.employment_status = employment_status
    
#     db.commit()
#     return RedirectResponse(url=f"/employees/{employee_id}", status_code=303)