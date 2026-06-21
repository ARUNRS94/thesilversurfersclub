import enum
from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Role(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    COMMUNITY_MANAGER = "community_manager"
    EVENT_COORDINATOR = "event_coordinator"
    FINANCE_MANAGER = "finance_manager"
    MEMBER = "member"

class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING_RENEWAL = "pending_renewal"

class RegistrationStatus(str, enum.Enum):
    REGISTERED = "registered"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"
    CONFIRMED = "confirmed"

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    users = relationship("User", back_populates="organization")
    members = relationship("Member", back_populates="organization")

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.MEMBER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    organization = relationship("Organization", back_populates="users")

class Member(Base, TimestampMixin):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    member_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    profile_photo: Mapped[str | None] = mapped_column(String(500))
    gender: Mapped[str | None] = mapped_column(String(40))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    blood_group: Mapped[str | None] = mapped_column(String(10))
    marital_status: Mapped[str | None] = mapped_column(String(40))
    mobile_number: Mapped[str] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    aadhaar_number: Mapped[str | None] = mapped_column(String(20))
    passport_number: Mapped[str | None] = mapped_column(String(30))
    passport_expiry_date: Mapped[date | None] = mapped_column(Date)
    pan_number: Mapped[str | None] = mapped_column(String(20))
    rtc_details: Mapped[str | None] = mapped_column(Text)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100))
    emergency_relationship: Mapped[str | None] = mapped_column(String(60))
    emergency_phone: Mapped[str | None] = mapped_column(String(30))
    medical_conditions: Mapped[str | None] = mapped_column(Text)
    allergies: Mapped[str | None] = mapped_column(Text)
    medications: Mapped[str | None] = mapped_column(Text)
    special_notes: Mapped[str | None] = mapped_column(Text)
    spouse_name: Mapped[str | None] = mapped_column(String(100))
    children_details: Mapped[str | None] = mapped_column(Text)
    organization = relationship("Organization", back_populates="members")
    memberships = relationship("Membership", back_populates="member", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="member")

class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    membership_number: Mapped[str] = mapped_column(String(50), unique=True)
    membership_type: Mapped[str] = mapped_column(String(40))
    join_date: Mapped[date] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[MembershipStatus] = mapped_column(Enum(MembershipStatus), default=MembershipStatus.ACTIVE)
    member = relationship("Member", back_populates="memberships")

class Event(Base, TimestampMixin):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    venue: Mapped[str] = mapped_column(String(255))
    event_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[str | None] = mapped_column(String(10))
    end_time: Mapped[str | None] = mapped_column(String(10))
    capacity: Mapped[int] = mapped_column(Integer)
    registration_deadline: Mapped[date | None] = mapped_column(Date)
    event_banner: Mapped[str | None] = mapped_column(String(500))
    registrations = relationship("EventRegistration", back_populates="event")

class EventRegistration(Base, TimestampMixin):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "member_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus), default=RegistrationStatus.REGISTERED)
    event = relationship("Event", back_populates="registrations")
    attendance = relationship("Attendance", back_populates="registration", uselist=False)

class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("event_registrations.id"))
    attended: Mapped[bool] = mapped_column(Boolean, default=False)
    method: Mapped[str | None] = mapped_column(String(40))
    registration = relationship("EventRegistration", back_populates="attendance")

class Trip(Base, TimestampMixin):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    destination: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    capacity: Mapped[int] = mapped_column(Integer)
    organizer: Mapped[str | None] = mapped_column(String(100))
    cost: Mapped[float] = mapped_column(Float, default=0)

class TripRegistration(Base, TimestampMixin):
    __tablename__ = "trip_registrations"
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus), default=RegistrationStatus.REGISTERED)
    amount_paid: Mapped[float] = mapped_column(Float, default=0)
    medical_notes: Mapped[str | None] = mapped_column(Text)

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"))
    title: Mapped[str] = mapped_column(String(200))
    document_type: Mapped[str] = mapped_column(String(80))
    file_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer, default=1)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    member = relationship("Member", back_populates="documents")

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    payment_for: Mapped[str] = mapped_column(String(40))
    amount: Mapped[float] = mapped_column(Float)
    payment_date: Mapped[date] = mapped_column(Date)
    payment_method: Mapped[str] = mapped_column(String(40))
    receipt_number: Mapped[str] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(40), default="paid")

class Announcement(Base, TimestampMixin):
    __tablename__ = "announcements"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), default="news")

class InterestGroup(Base, TimestampMixin):
    __tablename__ = "interest_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)

class GroupMembership(Base, TimestampMixin):
    __tablename__ = "group_memberships"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("interest_groups.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))

class GroupPost(Base, TimestampMixin):
    __tablename__ = "group_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("interest_groups.id"))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"))
    body: Mapped[str] = mapped_column(Text)

class NotificationTemplate(Base, TimestampMixin):
    __tablename__ = "notification_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(30), default="email")

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"))
    template_id: Mapped[int | None] = mapped_column(ForeignKey("notification_templates.id"))
    type: Mapped[str] = mapped_column(String(80))
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(30), default="email")
    status: Mapped[str] = mapped_column(String(30), default="queued")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    entity: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
