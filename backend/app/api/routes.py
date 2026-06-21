import csv
import io
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, require_roles
from app.core.security import create_access_token, verify_password
from app.db import get_db
from app.models import Document, Event, Member, Membership, MembershipStatus, Role, Trip, User
from app.schemas.common import DashboardKpis, EventCreate, LoginRequest, MemberCreate, MemberRead, Token, TripCreate
from app.services.dashboard import get_dashboard

router = APIRouter()

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
def list_members(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Member).order_by(Member.created_at.desc()).all()

@router.post("/members", response_model=MemberRead, tags=["Members"])
def create_member(payload: MemberCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER, Role.FINANCE_MANAGER))):
    next_id = db.query(Member).count() + 1
    member = Member(organization_id=user.organization_id, member_id=f"SC-{next_id:05d}", **payload.model_dump())
    db.add(member)
    db.flush()
    db.add(Membership(member_id=member.id, membership_number=f"MEM-{next_id:05d}", membership_type="Annual", join_date=date.today(), status=MembershipStatus.ACTIVE))
    db.commit()
    db.refresh(member)
    return member

@router.post("/events", tags=["Events"])
def create_event(payload: EventCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER, Role.EVENT_COORDINATOR))):
    event = Event(organization_id=user.organization_id, **payload.model_dump())
    db.add(event); db.commit(); db.refresh(event)
    return event

@router.get("/events", tags=["Events"])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Event).order_by(Event.event_date).all()

@router.post("/trips", tags=["Travel"])
def create_trip(payload: TripCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER))):
    trip = Trip(organization_id=user.organization_id, **payload.model_dump())
    db.add(trip); db.commit(); db.refresh(trip)
    return trip

@router.get("/trips", tags=["Travel"])
def list_trips(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Trip).order_by(Trip.start_date).all()

@router.post("/documents/upload", tags=["Documents"])
def upload_document(member_id: int, document_type: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    allowed = {"application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB")
    doc = Document(member_id=member_id, title=file.filename or document_type, document_type=document_type, file_path=f"uploads/{file.filename}", mime_type=file.content_type or "application/octet-stream", size_bytes=len(content))
    db.add(doc); db.commit(); db.refresh(doc)
    return doc

@router.get("/reports/{report_name}.csv", tags=["Reports"])
def report_csv(report_name: str, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.COMMUNITY_MANAGER, Role.FINANCE_MANAGER))):
    output = io.StringIO(); writer = csv.writer(output)
    if report_name == "members":
        writer.writerow(["member_id", "first_name", "last_name", "mobile", "email"])
        for m in db.query(Member).all(): writer.writerow([m.member_id, m.first_name, m.last_name, m.mobile_number, m.email])
    elif report_name == "events":
        writer.writerow(["name", "venue", "event_date", "capacity"])
        for e in db.query(Event).all(): writer.writerow([e.name, e.venue, e.event_date, e.capacity])
    else:
        raise HTTPException(status_code=404, detail="Unknown report")
    return Response(output.getvalue(), media_type="text/csv")
