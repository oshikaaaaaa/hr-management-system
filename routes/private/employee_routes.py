from fastapi import APIRouter, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
import json
from typing import Optional

from models import Employee, Department, Position
from enums import Gender, EmploymentStatus, PositionType
from base import SessionLocal

router = APIRouter(
    prefix="/employees",
    tags=["employees"]
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
async def list_employees(
    request: Request, 
    search: Optional[str] = None,
    search_field: Optional[str] = None,  # Add this parameter
    department_id: Optional[str] = None,
    position_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Start with a base query
    query = db.query(Employee)
    
    # Apply search filter if provided
    if search and search_field:
        search_term = f"%{search}%"
        
        # Apply search based on selected field
        if search_field == "employee_id":
            # For numeric fields, convert search to int if possible
            try:
                search_int = int(search)
                query = query.filter(Employee.employee_id == search_int)
            except ValueError:
                # If conversion fails, return empty result
                query = query.filter(Employee.employee_id == -1)  # This will return no results
        elif search_field == "first_name":
            query = query.filter(Employee.first_name.ilike(search_term))
        elif search_field == "last_name":
            query = query.filter(Employee.last_name.ilike(search_term))
        elif search_field == "department":
            query = query.join(Department).filter(Department.department_name.ilike(search_term))
        elif search_field == "position":
            query = query.join(Position).filter(Position.title.ilike(search_term))
    
    # Apply department filter if department is selected
    if department_id and department_id.isdigit():
        query = query.filter(Employee.department_id == int(department_id))
    
    # Apply position filter if position is selected
    if position_id and position_id.isdigit():
        query = query.filter(Employee.position_id == int(position_id))
    
    # Get the filtered employees
    employees = query.all()
    
    # Get the count of filtered employees
    employee_count = len(employees)
    
    # Get all departments and positions for the filter dropdowns
    departments = db.query(Department).all()
    positions = db.query(Position).all()
    
    return templates.TemplateResponse(
        "employees/list.html",
        {
            "request": request, 
            "employees": employees,
            "departments": departments,
            "positions": positions,
            "employee_count": employee_count,
            "search": search,
            "search_field": search_field
        }
    )

@router.get("/create", response_class=HTMLResponse)
async def create_employee_form(request: Request, db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    positions = db.query(Position).all()

    positions_data = [
        {
            'position_id': position.position_id,
            'title': position.title,
            'department_id': position.department_id
        }
        for position in positions
    ]
    
    positions_json = json.dumps(positions_data)
    
    return templates.TemplateResponse(
        "employees/create.html",
        {
            "request": request,
            "departments": departments,
            "positions": positions,
            "positions_json": positions_json
        }
    )

@router.post("/create")
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

@router.get("/{employee_id}", response_class=HTMLResponse)
async def read_employee(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        "employees/detail.html",
        {"request": request, "employee": employee}
    )

@router.get("/{employee_id}/edit", response_class=HTMLResponse)
async def edit_employee_form(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    departments = db.query(Department).all()
    positions = db.query(Position).all()
    
    return templates.TemplateResponse(
        "employees/edit.html",
        {
            "request": request, 
            "employee": employee,
            "departments": departments,
            "positions": positions
        }
    )

@router.post("/{employee_id}/edit")
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

@router.post("/{employee_id}/delete")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return RedirectResponse(url="/employees", status_code=303)