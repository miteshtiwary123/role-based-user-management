from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.schemas.common import Paginated, PageMeta
from app.crud import user as crud_user
from typing import List, Optional
from app.core.deps import get_db, get_current_user, require_role
from app.models.user import RoleEnum

router = APIRouter()

@router.post("/", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@router.get("/", response_model=Paginated[UserOut], dependencies=[Depends(get_current_user)])
def read_users(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, description="Search name or email"),
    role: Optional[RoleEnum] = Query(None, description="Filter by role"),
    sort_by: str = Query("id", pattern="^(id|name|email)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
):
    items, total = crud_user.get_users(
        db,
        limit=limit,
        offset=offset,
        q=q,
        role=role,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {"items": items, "meta": PageMeta(total=total, limit=limit, offset=offset)}

@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(get_current_user)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.get_user(db, user_id)

@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return crud_user.update_user(db, user_id, user)

@router.delete("/{user_id}", dependencies=[Depends(require_role(RoleEnum.admin))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.delete_user(db, user_id)
