from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import RoleEnum


class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[RoleEnum] = RoleEnum.user

class UserUpdate(UserBase):
    role: Optional[RoleEnum] = None

class UserOut(UserBase):
    id: int
    role: RoleEnum

    class Config:
        orm_mode = True
