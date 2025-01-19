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
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import HTMLResponse, RedirectResponse
import bcrypt  # Import bcrypt for password hashing
# Database setup
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Cooperation322060#@localhost:3306/management_system"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Enums
class Gender(str, enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class EmploymentStatus(str, enum.Enum):
    Active = "Active"
    Resigned = "Resigned"
    Terminated = "Terminated"
    On_Leave = "On_Leave"
    Absent = "Absent"

class PositionType(str, enum.Enum):
    Full = "Full"
    Part = "Part"

class LeaveStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

# Models
class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    hire_date = Column(Date)
    department_id = Column(Integer)
    position_id = Column(Integer)
    position_type = Column(Enum(PositionType))
    salary = Column(DECIMAL(10, 2))
    employment_status = Column(Enum(EmploymentStatus))

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100))
    hod_id = Column(Integer)
    dhod_id = Column(Integer)
    contact_number = Column(String(15))

class Position(Base):
    __tablename__ = "positions"
    
    position_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    base_salary_full = Column(DECIMAL(10, 2))
    base_salary_part = Column(DECIMAL(10, 2))
    allowances = Column(DECIMAL(10, 2))
    description = Column(Text)
    required_skills = Column(Text)

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

@app.get("/employees/create", response_class=HTMLResponse)
async def create_employee_form(request: Request):
    return templates.TemplateResponse(
        "employees/create.html",
        {"request": request}
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