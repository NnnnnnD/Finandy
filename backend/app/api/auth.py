from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.db import get_db
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "dev-secret"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def normalize_password(password: str) -> str:
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload["email"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(
        normalize_password(payload["password"]),
        user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.utcnow() + timedelta(hours=12),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.name,
        },
    }

@router.post("/logout")
def logout():
    res = Response()
    res.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
    )
    return {"status": "ok"}