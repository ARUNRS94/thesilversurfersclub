import csv
import io
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, require_roles
from app.core.security import create_access_token, verify_password
from app.db import get_db
from app.models import Announcement, Attendance, Document, Event, EventRegistration, InterestGroup, Member, Membership, MembershipStatus, Notification, Payment, RegistrationStatus, Role, Trip, TripRegistration, User
from app.schemas.common import AnnouncementCreate, DashboardKpis, EventCreate, InterestGroupCreate, LoginRequest, MemberCreate, MemberRead, MembershipCreate, NotificationCreate, PaymentCreate, Token, TripCreate
from app.services.dashboard import get_dashboard

router = APIRouter()
MANAGERS = (Role.COMMUNITY_MANAGER, Role.FINANCE_MANAGER)

@router.post("/auth/login", response_model=Token, tags=["Authentication"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.email, user.role.value))

@router.get("/dashboard", response_model=DashboardKpis, tags=["Dashboard"])
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_dashboard(db)

@router.get("/members", response_model=list[MemberRead], tags=["Members"])
def list_members(q: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Member)
    if q:
        like = f"%{q}%"
        query = query.filter((Member.first_name.ilike(like)) | (Member.last_name.ilike(like)) | (Member.member_id.ilike(like)) | (Member.mobile_number.ilike(like)))
    return query.order_by(Member.created_at.desc()).all()

@router.post("/members", response_model=MemberRead, tags=["Members"])
def create_member(payload: MemberCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    next_id = db.query(Member).count() + 1
    member = Member(organization_id=user.organization_id, member_id=f"SC-{next_id:05d}", **payload.model_dump())
    db.add(member); db.flush()
    db.add(Membership(member_id=member.id, membership_number=f"MEM-{next_id:05d}", membership_type="Annual", join_date=date.today(), status=MembershipStatus.ACTIVE))
    db.commit(); db.refresh(member)
    return member

@router.get("/members/{member_id}", tags=["Members"])
def get_member(member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    member = db.get(Member, member_id)
    if not member: raise HTTPException(404, "Member not found")
    return member

@router.put("/members/{member_id}", response_model=MemberRead, tags=["Members"])
def update_member(member_id: int, payload: MemberCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    member = db.get(Member, member_id)
    if not member: raise HTTPException(404, "Member not found")
    for key, value in payload.model_dump().items(): setattr(member, key, value)
    db.commit(); db.refresh(member)
    return member

@router.delete("/members/{member_id}", tags=["Members"])
def delete_member(member_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER))):
    member = db.get(Member, member_id)
    if not member: raise HTTPException(404, "Member not found")
    db.delete(member); db.commit()
    return {"ok": True}

@router.get("/memberships", tags=["Memberships"])
def list_memberships(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Membership).order_by(Membership.expiry_date).all()

@router.post("/memberships", tags=["Memberships"])
def create_membership(payload: MembershipCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    number = f"MEM-{db.query(Membership).count()+1:05d}"
    data = payload.model_dump(); data["status"] = MembershipStatus(data["status"]); membership = Membership(membership_number=number, **data)
    db.add(membership); db.commit(); db.refresh(membership)
    return membership

@router.put("/memberships/{membership_id}/renew", tags=["Memberships"])
def renew_membership(membership_id: int, expiry_date: date, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    membership = db.get(Membership, membership_id)
    if not membership: raise HTTPException(404, "Membership not found")
    membership.expiry_date = expiry_date; membership.status = MembershipStatus.ACTIVE
    db.commit(); db.refresh(membership)
    return membership

@router.get("/events", tags=["Events"])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Event).order_by(Event.event_date).all()

@router.post("/events", tags=["Events"])
def create_event(payload: EventCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER, Role.EVENT_COORDINATOR))):
    event = Event(organization_id=user.organization_id, **payload.model_dump())
    db.add(event); db.commit(); db.refresh(event)
    return event

@router.post("/events/{event_id}/register/{member_id}", tags=["Events"])
def register_event(event_id: int, member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    registered = db.query(EventRegistration).filter_by(event_id=event_id).count()
    status = RegistrationStatus.WAITLISTED if registered >= event.capacity else RegistrationStatus.REGISTERED
    reg = EventRegistration(event_id=event_id, member_id=member_id, status=status)
    db.add(reg); db.commit(); db.refresh(reg)
    return reg

@router.post("/events/registrations/{registration_id}/check-in", tags=["Events"])
def check_in(registration_id: int, method: str = "manual", db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER, Role.EVENT_COORDINATOR))):
    attendance = Attendance(registration_id=registration_id, attended=True, method=method)
    db.add(attendance); db.commit(); db.refresh(attendance)
    return attendance

@router.get("/trips", tags=["Travel"])
def list_trips(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Trip).order_by(Trip.start_date).all()

@router.post("/trips", tags=["Travel"])
def create_trip(payload: TripCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER))):
    trip = Trip(organization_id=user.organization_id, **payload.model_dump())
    db.add(trip); db.commit(); db.refresh(trip)
    return trip

@router.post("/trips/{trip_id}/register/{member_id}", tags=["Travel"])
def register_trip(trip_id: int, member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = db.get(Trip, trip_id)
    if not trip: raise HTTPException(404, "Trip not found")
    count = db.query(TripRegistration).filter_by(trip_id=trip_id).count()
    reg = TripRegistration(trip_id=trip_id, member_id=member_id, status=RegistrationStatus.WAITLISTED if count >= trip.capacity else RegistrationStatus.CONFIRMED)
    db.add(reg); db.commit(); db.refresh(reg)
    return reg

@router.get("/payments", tags=["Payments"])
def list_payments(db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    return db.query(Payment).order_by(Payment.payment_date.desc()).all()

@router.post("/payments", tags=["Payments"])
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    payment = Payment(receipt_number=f"RCT-{db.query(Payment).count()+1:06d}", **payload.model_dump())
    db.add(payment); db.commit(); db.refresh(payment)
    return payment

@router.get("/documents", tags=["Documents"])
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.post("/documents/upload", tags=["Documents"])
def upload_document(member_id: int, document_type: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    allowed = {"application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed: raise HTTPException(status_code=400, detail="Unsupported file type")
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024: raise HTTPException(status_code=400, detail="File size exceeds 10MB")
    doc = Document(member_id=member_id, title=file.filename or document_type, document_type=document_type, file_path=f"uploads/{file.filename}", mime_type=file.content_type or "application/octet-stream", size_bytes=len(content))
    db.add(doc); db.commit(); db.refresh(doc)
    return doc

@router.get("/announcements", tags=["Community"])
def list_announcements(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()

@router.post("/announcements", tags=["Community"])
def create_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER))):
    announcement = Announcement(organization_id=user.organization_id, **payload.model_dump())
    db.add(announcement); db.commit(); db.refresh(announcement)
    return announcement

@router.get("/groups", tags=["Community"])
def list_groups(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(InterestGroup).order_by(InterestGroup.name).all()

@router.post("/groups", tags=["Community"])
def create_group(payload: InterestGroupCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER))):
    group = InterestGroup(organization_id=user.organization_id, **payload.model_dump())
    db.add(group); db.commit(); db.refresh(group)
    return group

@router.get("/notifications", tags=["Notifications"])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Notification).order_by(Notification.created_at.desc()).all()

@router.post("/notifications", tags=["Notifications"])
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER))):
    note = Notification(**payload.model_dump())
    db.add(note); db.commit(); db.refresh(note)
    return note

@router.get("/reports/{report_name}.csv", tags=["Reports"])
def report_csv(report_name: str, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGERS))):
    output = io.StringIO(); writer = csv.writer(output)
    if report_name == "members":
        writer.writerow(["member_id", "first_name", "last_name", "mobile", "email"])
        for m in db.query(Member).all(): writer.writerow([m.member_id, m.first_name, m.last_name, m.mobile_number, m.email])
    elif report_name == "events":
        writer.writerow(["name", "venue", "event_date", "capacity"])
        for e in db.query(Event).all(): writer.writerow([e.name, e.venue, e.event_date, e.capacity])
    elif report_name == "payments":
        writer.writerow(["receipt", "member_id", "for", "amount", "date", "status"])
        for p in db.query(Payment).all(): writer.writerow([p.receipt_number, p.member_id, p.payment_for, p.amount, p.payment_date, p.status])
    elif report_name == "trips":
        writer.writerow(["name", "destination", "start", "end", "capacity", "cost"])
        for t in db.query(Trip).all(): writer.writerow([t.name, t.destination, t.start_date, t.end_date, t.capacity, t.cost])
    else:
        raise HTTPException(status_code=404, detail="Unknown report")
    return Response(output.getvalue(), media_type="text/csv")
