from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from fastapi import HTTPException
from typing import List, Optional, Tuple
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.models.user import RoleEnum

def create_user(db: Session, user: UserCreate):
    # check if email already exist
    if db.query(User).filter(User.email==user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role or RoleEnum.user,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    q: Optional[str] = None,
    role: Optional[RoleEnum] = None,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> Tuple[List[User], int]:
    query = db.query(User)

    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            func.lower(User.name).like(like) | func.lower(User.email).like(like)
        )
    if role:
        query = query.filter(User.role == role)

    sortable = {"id": User.id, "name": User.name, "email": User.email}
    sort_column = sortable.get(sort_by, User.id)
    order_fn = asc if sort_order.lower() == "asc" else desc
    query = query.order_by(order_fn(sort_column))

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user

def update_user(db: Session, user_id: int, payload: UserUpdate):
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    user.name = payload.name
    user.email = payload.email
    if payload.role:
        user.role = payload.role
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}