from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.app.core.config import settings
from src.app.db.session import get_db
from src.app.models.users import Users
from src.app.crud import users as crud_users
from src.app.schemas import token as token_schemas


token_url = (
    f"{settings.api_v1_str}/auth/login"
    if hasattr(settings, "api_v1_str")
    else "/auth/login"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Users:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[int] = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        token_data = token_schemas.TokenData(id=user_id)

    except JWTError:
        raise credentials_exception

    if token_data.id is None:
        raise credentials_exception

    user = crud_users.get_user_by_id(db, user_id=token_data.id)

    if user is None:
        raise credentials_exception

    return user
