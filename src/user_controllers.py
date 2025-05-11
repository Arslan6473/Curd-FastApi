from sqlalchemy.orm import Session
from . import models, schemas, security
from fastapi import HTTPException, status
from typing import List, Optional

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    # Check if user with the email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user object
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active
    )
    
    # Add to database and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    """Update a user by ID"""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Update user data
    update_data = user.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = security.get_password_hash(update_data.pop("password"))
    
    # Update user object
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Commit changes
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> models.User:
    """Delete a user by ID"""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Delete user from database
    db.delete(db_user)
    db.commit()
    return db_user
