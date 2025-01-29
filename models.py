import datetime
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Date, Boolean, DECIMAL, Enum, Text, Time
)
from sqlalchemy.orm import relationship
from base import Base  # ✅ Import Base from base.py
from enums import Gender, EmploymentStatus, PositionType, LeaveStatus, ApplicationStatus, InterviewStatus  # ✅ Import Enums

# Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(Date, default=datetime.datetime.now())
    last_login = Column(Date)

    conducted_interviews = relationship("Interview", back_populates="interviewer")

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    hire_date = Column(Date)
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    position_id = Column(Integer, ForeignKey("positions.position_id"))
    
    position_type = Column(Enum(PositionType))
    salary = Column(DECIMAL(10, 2))
    employment_status = Column(Enum(EmploymentStatus))

    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    leaves = relationship("Leave", back_populates="employee")
    leave_balance = relationship("LeaveBalance", back_populates="employee", uselist=False)
    payments = relationship("Payment", back_populates="employee")

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100))
    hod_id = Column(Integer)
    dhod_id = Column(Integer)
    contact_number = Column(String(15))

    positions = relationship("Position", back_populates="department")
    employees = relationship("Employee", back_populates="department")
    vacancies = relationship("Vacancy", back_populates="department")

class Position(Base):
    __tablename__ = "positions"
    
    position_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    base_salary_full = Column(DECIMAL(10, 2))
    base_salary_part = Column(DECIMAL(10, 2))
    allowances = Column(DECIMAL(10, 2))
    description = Column(Text)
    required_skills = Column(Text)

    department = relationship("Department", back_populates="positions")
    employees = relationship("Employee", back_populates="position")
    vacancies = relationship("Vacancy", back_populates="position")

class Leave(Base):
    __tablename__ = "leaves"
    
    leave_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    is_paid = Column(Boolean)
    status = Column(Enum(LeaveStatus))
    purpose = Column(String(255))

    employee = relationship("Employee", back_populates="leaves")

class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    
    balance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    paid_leave_balance = Column(Integer)
    unpaid_leave_balance = Column(Integer)

    employee = relationship("Employee", back_populates="leave_balance")

class Payment(Base):
    __tablename__ = "payments"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    pending_salary = Column(DECIMAL(10, 2))
    last_payment_date = Column(Date)
    appraisal_date = Column(Date)
    adjustments = Column(DECIMAL(10, 2))

    employee = relationship("Employee", back_populates="payments")

class Applicant(Base):
    __tablename__ = "applicants"
    
    applicant_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    contact_number = Column(String(15))
    email = Column(String(100))
    vacancy_id = Column(Integer, ForeignKey("vacancies.vacancy_id"))
    status = Column(Enum(ApplicationStatus))
    resume_url = Column(String(255))
    application_date = Column(Date)

    vacancy = relationship("Vacancy", back_populates="applicants")
    interviews = relationship("Interview", back_populates="applicant")
    # interview_status = Column(String)  # Could be enum: Pending, Completed, Rescheduled, Cancelled

class Interview(Base):
    __tablename__ = "interviews"
    
    interview_id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.applicant_id"))
    interview_date = Column(Date)
    interview_time = Column(Time)
    interview_status = Column(Enum(InterviewStatus))
    interviewed_by = Column(Integer, ForeignKey("users.user_id"))
    interview_notes = Column(Text)

    applicant = relationship("Applicant", back_populates="interviews")
    interviewer = relationship("User", back_populates="conducted_interviews")

class Vacancy(Base):
    __tablename__ = "vacancies"
    
    vacancy_id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    position_id = Column(Integer, ForeignKey("positions.position_id"))
    position_title = Column(String(100))
    job_description = Column(Text)
    required_skills = Column(Text)
    open_date = Column(Date)
    is_open = Column(Boolean, default=True)

    department = relationship("Department", back_populates="vacancies")
    position = relationship("Position", back_populates="vacancies")
    applicants = relationship("Applicant", back_populates="vacancy")
