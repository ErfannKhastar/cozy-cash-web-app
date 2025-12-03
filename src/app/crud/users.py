from sqlalchemy.orm import Session
from src.app.models.users import Users
from src.app.schemas.users import UserCreate
from src.app.core.security import hash_password


def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(Users).filter(Users.id == user_id).first()


def create_user(db: Session, user: UserCreate):
    hashed_pwd = hash_password(user.password)
    db_user = Users(email=user.email, password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
