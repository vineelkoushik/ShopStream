from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User
from app.schemas import UserCreate
from app.security import hash_password

def create_user(db: Session, user_in: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    new_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role="customer"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    return user