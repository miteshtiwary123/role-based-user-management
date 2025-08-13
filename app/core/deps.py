from fastapi import Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.core.security import decode_token, TokenExpire, TokenError, create_access_token
from app.db.session import SessionLocal
from app.models.user import User, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _extract_bearer(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def get_current_user(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    header_token: Optional[str] = Depends(oauth2_scheme)
):
    token = header_token or request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = None
    try:
        payload = decode_token(token)
    except TokenExpire:
        # Try with refresh cookie
        refresh = request.cookies.get("refresh_token")
        if not refresh:
            raise HTTPException(status_code=401, detail="Access token expired")

        # Validate refresh token
        try:
            r_payload = decode_token(refresh)
        except TokenExpire:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except TokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if r_payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

        user_id = int(r_payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="user not found")

        # Mint new access token and set cookies
        new_access = create_access_token({"sub": str(user.id), "role": user.role})
        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )
        response.headers["X-New-Access-Token"] = new_access
        payload = {"sub": str(user.id), "role": user.role, "type": "access"}

    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user

def require_role(required_role: RoleEnum):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_checker