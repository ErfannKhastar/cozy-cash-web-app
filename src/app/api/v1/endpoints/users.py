from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.schemas import users as user_schemas
from src.app.crud import users as crud_users
from src.app.api import deps
from src.app.models.users import Users


router = APIRouter()


@router.post(
    "/", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user_in: user_schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud_users.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_users.create_user(db, user=user_in)
    return user


@router.get("/me", response_model=user_schemas.UserResponse)
def read_users_me(current_user: Users = Depends(deps.get_current_user)):
    return current_user
