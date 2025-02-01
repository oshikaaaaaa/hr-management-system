# main.py
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.orm import sessionmaker, relationship
  # Import bcrypt for password hashing

from enums import Gender, EmploymentStatus, PositionType, LeaveStatus, ApplicationStatus,InterviewStatus

from base import engine, Base,SessionLocal
#from auth import auth_middleware, get_current_user  # Add get_current_user here

from routes.public import (dashboard_routes,department_list_routes,job_listing_routes,postion_list_routes)

from routes.shared import (
  about_routes,
  contact_routes)
from routes.private import (
    employee_routes,
    department_routes,
    leave_routes,
    auth_routes,
    position_routes,
    vacancy_routes,
    applicant_routes,
    interview_routes,
    payment_routes,
    dashboard_routes
)


# from auth import auth_middleware
from routes.public import department_list_routes

# FastAPI app setup
app = FastAPI()

# Add middleware
# app.middleware("http")(auth_middleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)



# public routes
app.include_router(auth_routes.router)
app.include_router(department_list_routes.router)
app.include_router(job_listing_routes.router)
app.include_router(postion_list_routes.router)
# app.include_router(.router)



#app.include_router(departments_public_routes.router)

#shared routes
app.include_router(about_routes.router)
app.include_router(contact_routes.router)

#private routes
app.include_router(dashboard_routes.router)
app.include_router(employee_routes.router)
app.include_router(department_routes.router)
app.include_router(leave_routes.router)
app.include_router(position_routes.router)
app.include_router(vacancy_routes.router)
app.include_router(applicant_routes.router)
app.include_router(interview_routes.router)
app.include_router(payment_routes.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("public/public_dashboard.html", {"request": request})
