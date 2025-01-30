from models import User
from base import SessionLocal
from auth import get_password_hash
import datetime

def create_initial_user():
    db = SessionLocal()
    
    admin_user = User(
        username="admin",
        password=get_password_hash("your-secure-password"),  # Hash the password
        is_admin=True,  # Set admin user
        created_at=datetime.datetime.now(),  # Set created timestamp
        last_login=None  # No login yet
    )
    
    db.add(admin_user)
    db.commit()
    db.close()

if __name__ == "__main__":
    create_initial_user()
