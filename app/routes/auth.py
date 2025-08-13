from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenError,
    TokenExpire,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

COOKIE_COMMON = dict(httponly=True, secure=False, samesite="lax", path="/")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email==form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role})

    response.set_cookie("access_token", access_token, **COOKIE_COMMON)
    response.set_cookie("refresh_token", refresh_token, **COOKIE_COMMON)

    return{
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str, response: Response, db: Session = Depends(get_db)):
    """
    Accepts a refresh token and returns a new access token.
    """
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid refresh token type")
    except TokenExpire:
        raise HTTPException(status_code=401, detail="Refresh Token Expired")
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token({"sub": str(user.id), "role": user.role})
    response.set_cookie("access_token", new_access_token, **COOKIE_COMMON)
    response.headers["X-New-Access-Token"] = new_access_token
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}
