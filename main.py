# main.py
import json
import enum
import datetime
import bcrypt

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, Text, Enum, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, time
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
  # Import bcrypt for password hashing

from enums import Gender, EmploymentStatus, PositionType, LeaveStatus, ApplicationStatus,InterviewStatus
from models import User, Employee, Department, Position, Leave, LeaveBalance, Payment, Applicant, Interview, Vacancy
from base import engine, Base,SessionLocal

from routes import (
    employee_routes,
    department_routes,
    leave_routes,
    auth_routes,
    position_routes,
    vacancy_routes,
    applicant_routes,
    interview_routes,
    payment_routes
)
from auth import auth_middleware

# FastAPI app setup
app = FastAPI()

# Add middleware
#app.middleware("http")(auth_middleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_routes.router)
app.include_router(employee_routes.router)
app.include_router(department_routes.router)
app.include_router(leave_routes.router)
app.include_router(position_routes.router)
app.include_router(vacancy_routes.router)
app.include_router(applicant_routes.router)
app.include_router(interview_routes.router)
app.include_router(payment_routes.router)

# Root route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

