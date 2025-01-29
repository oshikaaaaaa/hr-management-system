# main.py

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, Text, Enum, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, time
import enum
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
import datetime
import bcrypt  # Import bcrypt for password hashing

from enums import Gender, EmploymentStatus, PositionType, LeaveStatus, ApplicationStatus,InterviewStatus
from models import User, Employee, Department, Position, Leave, LeaveBalance, Payment, Applicant, Interview, Vacancy
from base import engine, Base,SessionLocal



    # interview_status = Column(String)  # Could be enum: Pending, Completed, Rescheduled, Cancelled


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app setup
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Employee routes
@app.get("/employees", response_class=HTMLResponse)
async def list_employees(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse(
        "employees/list.html",
        {"request": request, "employees": employees}
    )

import json
@app.get("/employees/create", response_class=HTMLResponse)
async def create_employee_form(request: Request, db: Session = Depends(get_db)):
    # Fetch all departments and positions from the database
    departments = db.query(Department).all()
    positions = db.query(Position).all()

    positions_data = [
        {
            'position_id': position.position_id,
            'title': position.title,
            'department_id': position.department_id  # Make sure this matches exactly with your model
        }
        for position in positions
    ]
    
    # Convert to JSON
    positions_json = json.dumps(positions_data)
    
    # Print for debugging
    print("Positions data:", positions_json)

    
    return templates.TemplateResponse(
        "employees/create.html",
        {
            "request": request,
            "departments": departments,
            "positions": positions,

            "positions_json": positions_json
        }
    )

@app.post("/employees/create")
async def create_employee(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: date = Form(...),
    gender: Gender = Form(...),
    hire_date: date = Form(...),
    department_id: int = Form(...),
    position_id: int = Form(...),
    position_type: PositionType = Form(...),
    salary: float = Form(...),
    employment_status: EmploymentStatus = Form(...),
    db: Session = Depends(get_db)
):
    # Verify that department and position exist
    department = db.query(Department).filter(Department.department_id == department_id).first()
    position = db.query(Position).filter(Position.position_id == position_id).first()
    

    
    if not department or not position:
        raise HTTPException(status_code=400, detail="Invalid department or position")
    
    try:
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            hire_date=hire_date,
            department_id=department_id,
            position_id=position_id,
            position_type=position_type,
            salary=salary,
            employment_status=employment_status
        )
        db.add(employee)
        db.commit()
        return RedirectResponse(url="/employees", status_code=303)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")

@app.get("/employees/{employee_id}", response_class=HTMLResponse)
async def read_employee(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        "employees/detail.html",
        {"request": request, "employee": employee}
    )

@app.get("/employees/{employee_id}/edit", response_class=HTMLResponse)
async def edit_employee_form(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        "employees/edit.html",
        {"request": request, "employee": employee}
    )

@app.post("/employees/{employee_id}/edit")
async def edit_employee(
    request: Request,
    employee_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: date = Form(...),
    gender: Gender = Form(...),
    hire_date: date = Form(...),
    department_id: int = Form(...),
    position_id: int = Form(...),
    position_type: PositionType = Form(...),
    salary: float = Form(...),
    employment_status: EmploymentStatus = Form(...),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    employee.first_name = first_name
    employee.last_name = last_name
    employee.date_of_birth = date_of_birth
    employee.gender = gender
    employee.hire_date = hire_date
    employee.department_id = department_id
    employee.position_id = position_id
    employee.position_type = position_type
    employee.salary = salary
    employee.employment_status = employment_status
    
    db.commit()
    return RedirectResponse(url=f"/employees/{employee_id}", status_code=303)

@app.post("/employees/{employee_id}/delete")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return RedirectResponse(url="/employees", status_code=303)



@app.get("/departments", response_class=HTMLResponse)
async def list_departments(request: Request, db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    return templates.TemplateResponse(
        "departments/list.html",
        {"request": request, "departments": departments}
    )

@app.get("/departments/create", response_class=HTMLResponse)
async def create_department_form(request: Request):
    return templates.TemplateResponse(
        "departments/create.html",
        {"request": request}
    )

@app.post("/departments/create")
async def create_department(
    request: Request,
    department_name: str = Form(...),
    hod_id: int = Form(...),
    dhod_id: int = Form(...),
    contact_number: str = Form(...),
    db: Session = Depends(get_db)
):
    department = Department(
        department_name=department_name,
        hod_id=hod_id,
        dhod_id=dhod_id,
        contact_number=contact_number
    )
    db.add(department)
    db.commit()
    return RedirectResponse(url="/departments", status_code=303)

@app.get("/departments/{department_id}", response_class=HTMLResponse)
async def read_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return templates.TemplateResponse(
        "departments/detail.html",
        {"request": request, "department": department}
    )

@app.get("/departments/{department_id}/edit", response_class=HTMLResponse)
async def edit_department_form(request: Request, department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return templates.TemplateResponse(
        "departments/edit.html",
        {"request": request, "department": department}
    )

@app.post("/departments/{department_id}/edit")
async def edit_department(
    request: Request,
    department_id: int,
    department_name: str = Form(...),
    hod_id: int = Form(...),
    dhod_id: int = Form(...),
    contact_number: str = Form(...),
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    department.department_name = department_name
    department.hod_id = hod_id
    department.dhod_id = dhod_id
    department.contact_number = contact_number
    
    db.commit()
    return RedirectResponse(url=f"/departments/{department_id}", status_code=303)

@app.post("/departments/{department_id}/delete")
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(department)
    db.commit()
    return RedirectResponse(url="/departments", status_code=303)

# Position routes
@app.get("/positions", response_class=HTMLResponse)
async def list_positions(request: Request, db: Session = Depends(get_db)):
    positions = db.query(Position).all()
    return templates.TemplateResponse(
        "positions/list.html",
        {"request": request, "positions": positions}
    )

@app.get("/positions/create", response_class=HTMLResponse)
async def create_position_form(request: Request):
    return templates.TemplateResponse(
        "positions/create.html",
        {"request": request}
    )

@app.post("/positions/create")
async def create_position(
    request: Request,
    title: str = Form(...),
    base_salary_full: float = Form(...),
    department_id : int = Form(...),
    base_salary_part: float = Form(...),
    allowances: float = Form(...),
    description: str = Form(...),
    required_skills: str = Form(...),
    db: Session = Depends(get_db)
):
    position = Position(
        title=title,
        base_salary_full=base_salary_full,
        base_salary_part=base_salary_part,
        allowances=allowances,
        description=description,
        department_id = department_id,
        required_skills=required_skills
    )
    db.add(position)
    db.commit()
    return RedirectResponse(url="/positions", status_code=303)

@app.get("/positions/{position_id}", response_class=HTMLResponse)
async def read_position(request: Request, position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return templates.TemplateResponse(
        "positions/detail.html",
        {"request": request, "position": position}
    )

@app.get("/positions/{position_id}/edit", response_class=HTMLResponse)
async def edit_position_form(request: Request, position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return templates.TemplateResponse(
        "positions/edit.html",
        {"request": request, "position": position}
    )

@app.post("/positions/{position_id}/edit")
async def edit_position(
    request: Request,
    position_id: int,
    title: str = Form(...),
    base_salary_full: float = Form(...),
    base_salary_part: float = Form(...),
    allowances: float = Form(...),
    description: str = Form(...),
    required_skills: str = Form(...),
    db: Session = Depends(get_db)
):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    
    position.title = title
    position.base_salary_full = base_salary_full
    position.base_salary_part = base_salary_part
    position.allowances = allowances
    position.description = description
    position.required_skills = required_skills
    
    db.commit()
    return RedirectResponse(url=f"/positions/{position_id}", status_code=303)

@app.post("/positions/{position_id}/delete")
async def delete_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(position)
    db.commit()
    return RedirectResponse(url="/positions", status_code=303)


@app.get("/leaves", response_class=HTMLResponse)
async def list_leaves(request: Request, db: Session = Depends(get_db)):
    leaves = db.query(Leave).all()
    return templates.TemplateResponse(
        "leaves/list.html",
        {"request": request, "leaves": leaves}
    )

@app.get("/leaves/create", response_class=HTMLResponse)
async def create_leave_form(request: Request,db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse(
        "leaves/create.html",
        {"request": request,
         "employees":employees}
    )

@app.post("/leaves/create")
async def create_leave(
    request: Request,
    employee_id: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    is_paid: bool = Form(...),
    status: LeaveStatus = Form(...),
    purpose: str = Form(...),
    db: Session = Depends(get_db)
):
    leave = Leave(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        is_paid=is_paid,
        status=status,
        purpose=purpose
    )

    db.add(leave)
    

    today = date.today()
    if (status == 'Approved' and 
        start_date <= today <= end_date):
        
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        
        if employee:
            # Check for any other active approved leaves in this period
            other_active_leaves = db.query(Leave).filter(
                Leave.employee_id == employee_id,
                Leave.status == 'Approved',
                Leave.start_date <= today,
                Leave.end_date >= today,
                Leave.leave_id != leave.leave_id
            ).first()
            
            if not other_active_leaves:
                employee.employment_status = EmploymentStatus.On_Leave

    db.commit()
    return RedirectResponse(url="/leaves", status_code=303)

# Vacancy routes
@app.get("/vacancies", response_class=HTMLResponse)
async def list_vacancies(request: Request, db: Session = Depends(get_db)):
    vacancies = db.query(Vacancy).all()
    return templates.TemplateResponse(
        "vacancies/list.html",
        {"request": request, "vacancies": vacancies}
    )


@app.get("/vacancies/create", response_class=HTMLResponse)
async def create_position_form(request: Request):
    return templates.TemplateResponse(
        "vacancies/create.html",
        {"request": request}
    )

@app.post("/vacancies/create")
async def create_vacancy(
    request: Request,
    department_id: int = Form(...),
    position_id: int = Form(...),
    position_title: str = Form(...),
    job_description: str = Form(...),
    required_skills: str = Form(...),
    open_date: date = Form(...),
    is_open: bool = Form(True),
    db: Session = Depends(get_db)
):
    vacancy = Vacancy(
        department_id=department_id,
        position_id=position_id,
        position_title=position_title,
        job_description=job_description,
        required_skills=required_skills,
        open_date=open_date,
        is_open=is_open
    )
    db.add(vacancy)
    db.commit()
    return RedirectResponse(url="/vacancies", status_code=303)

@app.post("/vacancies/{vacancy_id}/delete")
async def delete_position(vacancy_id: int, db: Session = Depends(get_db)):
    id = db.query(Vacancy).filter(Vacancy.vacancy_id == vacancy_id).first()
    if id is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(id)
    db.commit()
    return RedirectResponse(url="/vacancies", status_code=303)

# Applicant routes
@app.get("/applicants", response_class=HTMLResponse)
async def list_applicants(request: Request, db: Session = Depends(get_db)):
    applicants = db.query(Applicant).all()
    return templates.TemplateResponse(
        "applicants/list.html",
        {"request": request, "applicants": applicants}
    )


@app.get("/applicants/create", response_class=HTMLResponse)
async def list_applicants(request: Request, db: Session = Depends(get_db)):
    applicants = db.query(Applicant).all()
    return templates.TemplateResponse(
        "applicants/create.html",
        {"request": request, "applicants": applicants}
    )
@app.post("/applicants/create")
async def create_applicant(
    request: Request,
    full_name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    vacancy_id: int = Form(...),
    resume_url: str = Form(...),
    db: Session = Depends(get_db)
):
    applicant = Applicant(
        full_name=full_name,
        contact_number=contact_number,
        email=email,
        vacancy_id=vacancy_id,
        status="Pending",
        resume_url=resume_url,
        application_date=date.today()
    )
    db.add(applicant)
    db.commit()
    return RedirectResponse(url="/applicants", status_code=303)

# Interview routes
@app.get("/interviews", response_class=HTMLResponse)
async def list_interviews(request: Request, db: Session = Depends(get_db)):
    interviews = db.query(Interview).all()
    return templates.TemplateResponse(
        "interviews/list.html",
        {"request": request, "interviews": interviews}
    )

@app.post("/interviews/create")
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

# Payment routes
@app.get("/payments", response_class=HTMLResponse)
async def list_payments(request: Request, db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return templates.TemplateResponse(
        "payments/list.html",
        {"request": request, "payments": payments}
    )

@app.post("/payments/create")
async def create_payment(
    request: Request,
    employee_id: int = Form(...),
    pending_salary: float = Form(...),
    last_payment_date: date = Form(...),
    appraisal_date: date = Form(...),
    adjustments: float = Form(0.0),
    db: Session = Depends(get_db)
):
    payment = Payment(
        employee_id=employee_id,
        pending_salary=pending_salary,
        last_payment_date=last_payment_date,
        appraisal_date=appraisal_date,
        adjustments=adjustments
    )
    db.add(payment)
    db.commit()
    return RedirectResponse(url="/payments", status_code=303)