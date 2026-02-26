from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.post('', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail='Email already exists')

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        english_level=payload.english_level,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get('', response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(select(User).order_by(User.id.asc())).all())


@router.get('/me', response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put('/me', response_model=UserRead)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.english_level is not None:
        current_user.english_level = payload.english_level
    if payload.is_active is not None:
        current_user.is_active = payload.is_active

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
