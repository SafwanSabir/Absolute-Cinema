from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from backend.src.database import get_db
from backend.src.auth import schemas, service
from backend.src.auth.models import User
from backend.src.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    success = service.register_new_user(db, user.username, user.email, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_id = service.authenticate_user(db, user.username, user.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/reset-password-request")
def reset_password_request(req: schemas.PasswordResetRequest):
    success = service.send_reset_email(req.email)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send reset email")
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
def reset_password(req: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    email = service.verify_reset_token(req.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    success = service.reset_user_password(db, email, req.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="User not found")
    
    return {"message": "Password updated successfully"}
