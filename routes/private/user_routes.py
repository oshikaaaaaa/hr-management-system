from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from auth import get_current_user, get_db
from models import User
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    users = db.query(User).all()
    admin_count = db.query(func.count(User.user_id)).filter(User.is_admin == True).scalar()
    
    return templates.TemplateResponse(
        "users/user_list.html", 
        {
            "request": request,
            "users": users,
            "user": current_user,
            "admin_count": admin_count
        }
    )

@router.get("/users/add", response_class=HTMLResponse)
async def add_user_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse(
        "users/add_user.html", 
        {
            "request": request,
            "user": current_user
        }
    )

@router.post("/users/add")
async def add_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    is_admin: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    try:
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        # Create new user
        new_user = User(
            username=username, 
            password=hashed_password, 
            is_admin=is_admin
        )
        
        db.add(new_user)
        db.commit()
        
        return RedirectResponse(url="/users", status_code=303)
    
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            "users/add_user.html", 
            {
                "request": request,
                "error": "Username already exists",
                "user": current_user
            }
        )
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "users/add_user.html", 
            {
                "request": request,
                "error": str(e),
                "user": current_user
            }
        )

@router.post("/users/delete/{user_id}")
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    # Find the user to delete
    user_to_delete = db.query(User).filter(User.user_id == user_id).first()
    
    if not user_to_delete:
        return RedirectResponse(url="/users", status_code=303)
    
    # Check if trying to delete the last admin
    admin_count = db.query(func.count(User.user_id)).filter(User.is_admin == True).scalar()
    
    if user_to_delete.is_admin and admin_count <= 1:
        # Cannot delete the last admin
        return templates.TemplateResponse(
            "users/user_list.html", 
            {
                "request": request,
                "error": "Cannot delete the last admin user",
                "users": db.query(User).all(),
                "user": current_user,
                "admin_count": admin_count
            }
        )
    
    try:
        # Delete the user
        db.delete(user_to_delete)
        db.commit()
        return RedirectResponse(url="/users", status_code=303)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "users/user_list.html", 
            {
                "request": request,
                "error": f"Error deleting user: {str(e)}",
                "users": db.query(User).all(),
                "user": current_user,
                "admin_count": admin_count
            }
        )