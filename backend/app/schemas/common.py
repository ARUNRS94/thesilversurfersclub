from datetime import date
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    mobile_number: str
    email: EmailStr | None = None
    date_of_birth: date | None = None
    city: str | None = None

class MemberRead(MemberCreate):
    id: int
    member_id: str
    model_config = {"from_attributes": True}

class EventCreate(BaseModel):
    name: str
    venue: str
    event_date: date
    capacity: int
    description: str | None = None

class TripCreate(BaseModel):
    name: str
    destination: str
    start_date: date
    end_date: date
    capacity: int
    cost: float = 0

class DashboardKpis(BaseModel):
    total_members: int
    active_members: int
    expired_memberships: int
    renewals_due: int
    upcoming_events: int
    event_registrations: int
    attendance_rate: float
    upcoming_trips: int
    birthdays_this_month: int
