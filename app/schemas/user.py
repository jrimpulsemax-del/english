from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    english_level: str = 'A1'


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    english_level: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
