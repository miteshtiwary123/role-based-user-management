from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.crud import user as crud_user
from typing import List
from app.core.deps import get_db, get_current_user, require_role
from app.models.user import RoleEnum

router = APIRouter()

@router.post("/", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@router.get("/", response_model=List[UserOut], dependencies=[Depends(get_current_user)])
def read_user(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_user.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(get_current_user)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.get_user(db, user_id)

@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return crud_user.update_user(db, user_id, user)

@router.delete("/{user_id}", dependencies=[Depends(require_role(RoleEnum.admin))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.delete_user(db, user_id)
