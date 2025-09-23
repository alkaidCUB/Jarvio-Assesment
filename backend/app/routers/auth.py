from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Mock login endpoint - accepts demo credentials or creates user, returns JWT"""
    # Demo credentials
    demo_email = "demo@example.com"
    demo_password = "demo123"
    
    # Check if it's demo login
    if login_request.email == demo_email and login_request.password == demo_password:
        # Find or create demo user
        user = db.query(models.User).filter(models.User.email == demo_email).first()
        if not user:
            user = models.User(
                email=demo_email,
                name="Demo User"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        # For other emails, create user automatically (mock behavior)
        user = db.query(models.User).filter(models.User.email == login_request.email).first()
        if not user:
            user = models.User(
                email=login_request.email,
                name=login_request.email.split("@")[0].title()  # Use email prefix as name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    """Get current user information"""
    return current_user