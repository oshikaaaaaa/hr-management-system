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
  
from fastapi.middleware.cors import CORSMiddleware

from base import engine, Base, SessionLocal
from auth import auth_middleware, get_current_user


from routes.public import (dashboard_routes,department_list_routes,job_listing_routes,postion_list_routes,                           interviews_dates_routes, about_routes,
  contact_routes,
login_routes
)


from routes.private import (
    employee_routes,
    department_routes,
    leave_routes,
    position_routes,
    vacancy_routes,
    applicant_routes,
    interview_routes,
    payment_routes,
    dashboard_routes,
    
)


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Add authentication middleware
app.middleware("http")(auth_middleware)



# Create database tables
Base.metadata.create_all(bind=engine)

# Public routes (no authentication required)
app.include_router(department_list_routes.router)
app.include_router(job_listing_routes.router)
app.include_router(postion_list_routes.router)
app.include_router(interviews_dates_routes.router)
app.include_router(login_routes.router)

# Shared routes (no authentication required)
app.include_router(about_routes.router)
app.include_router(contact_routes.router)

# Private routes (authentication required)
# Add dependencies to each private router
app.include_router(
    dashboard_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    employee_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    department_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    leave_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    position_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    vacancy_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    applicant_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    interview_routes.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    payment_routes.router,
    dependencies=[Depends(get_current_user)]
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("public/public_dashboard.html", {"request": request})