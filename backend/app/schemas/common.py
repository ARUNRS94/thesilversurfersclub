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
    gender: str | None = None
    blood_group: str | None = None
    marital_status: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    emergency_contact_name: str | None = None
    emergency_relationship: str | None = None
    emergency_phone: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None
    medications: str | None = None
    special_notes: str | None = None

class MemberRead(MemberCreate):
    id: int
    member_id: str
    model_config = {"from_attributes": True}

class MembershipCreate(BaseModel):
    member_id: int
    membership_type: str = "Annual"
    join_date: date
    expiry_date: date | None = None
    status: str = "active"

class EventCreate(BaseModel):
    name: str
    venue: str
    event_date: date
    capacity: int
    description: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    registration_deadline: date | None = None

class TripCreate(BaseModel):
    name: str
    destination: str
    start_date: date
    end_date: date
    capacity: int
    cost: float = 0
    organizer: str | None = None
    description: str | None = None

class PaymentCreate(BaseModel):
    member_id: int
    payment_for: str
    amount: float
    payment_date: date
    payment_method: str
    status: str = "paid"

class AnnouncementCreate(BaseModel):
    title: str
    body: str
    category: str = "news"

class InterestGroupCreate(BaseModel):
    name: str
    description: str | None = None

class NotificationCreate(BaseModel):
    member_id: int | None = None
    type: str
    subject: str
    body: str
    channel: str = "email"

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
