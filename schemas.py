from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool = False

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    venue: str
    event_date: str


class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    venue: str
    event_date: str
    organizer_id: int

    class Config:
        from_attributes = True


class TicketOut(BaseModel):
    id: int
    code: str
    user_id: int
    event_id: int
    is_used: bool

    class Config:
        from_attributes = True