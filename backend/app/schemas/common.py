from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator

class StrictBaseModel(BaseModel):
    @field_validator('*', mode='before')
    @classmethod
    def reject_blank_mandatory_strings(cls, value):
        if isinstance(value, str) and value.strip() == '':
            return None
        return value

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str
    password: str

class CurrentUserRead(BaseModel):
    email: str
    role: str
    is_active: bool
    allowed_pages: list[str] = []

class AdminUserCreate(StrictBaseModel):
    email: EmailStr
    password: str | None = None
    role: str
    is_active: bool = True
    allowed_pages: list[str] = []

class AdminUserRead(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    allowed_pages: list[str] = []
    model_config = {"from_attributes": True}

class MemberCreate(StrictBaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    mobile_number: str = Field(min_length=1)
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
    aadhaar_number: str | None = None
    passport_number: str | None = None
    passport_expiry_date: date | None = None
    pan_number: str | None = None
    rtc_details: str | None = None
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

class MembershipTypeCreate(StrictBaseModel):
    name: str = Field(min_length=1)
    duration_days: int = Field(gt=0)
    fee: float = 0
    description: str | None = None
    is_active: bool = True

class MembershipCreate(StrictBaseModel):
    member_id: int = Field(gt=0)
    membership_type: str = Field(default="Annual", min_length=1)
    join_date: date
    expiry_date: date | None = None
    status: str = "active"

class EventCreate(StrictBaseModel):
    name: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    event_date: date
    capacity: int = Field(gt=0)
    description: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    registration_deadline: date | None = None

class TripCreate(StrictBaseModel):
    name: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    start_date: date
    end_date: date
    capacity: int = Field(gt=0)
    cost: float = 0
    organizer: str | None = None
    description: str | None = None

class PaymentCreate(StrictBaseModel):
    member_id: int = Field(gt=0)
    payment_for: str = Field(min_length=1)
    amount: float = Field(gt=0)
    payment_date: date
    payment_method: str = Field(min_length=1)
    status: str = "paid"

class AnnouncementCreate(StrictBaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    category: str = "news"

class InterestGroupCreate(StrictBaseModel):
    name: str = Field(min_length=1)
    description: str | None = None

class NotificationCreate(StrictBaseModel):
    member_id: int | None = None
    type: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
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
