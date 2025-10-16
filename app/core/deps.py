from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.engine import get_session
from app.db.models import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

# DB session dependency
def get_db() -> Generator[Session, None, None]:
    with get_session() as db:
        yield db

# Current user dependency
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception


    user = db.query(User).filter(User.email == subject).first()
    if not user or not user.is_active:
        raise credentials_exception
    return user