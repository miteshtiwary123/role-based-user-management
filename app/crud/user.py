from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    hashed_password = user.password + "notreallyhashed"
    db_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int= 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id==user_id).first()

def update_user(db: Session, user_id: int, name: str, email: str):
    user = db.query(User).filter(User.id==user_id).first()
    if user:
        user.name = name
        user.email = email
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id==user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user