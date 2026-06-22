from datetime import date, timedelta
from app.core.security import hash_password, verify_password
from app.db import Base, SessionLocal, engine
from app.models import Event, InterestGroup, Member, Membership, MembershipStatus, NotificationTemplate, Organization, Role, Trip, User

Base.metadata.create_all(bind=engine)
db = SessionLocal()
org = db.query(Organization).first() or Organization(name="The Silver Surfers Club")
db.add(org); db.flush()

DEFAULT_ADMIN_EMAIL = "admin@seniorconnect.local"
DEFAULT_ADMIN_PASSWORD = "Admin123!"
admin = db.query(User).filter(User.email.ilike(DEFAULT_ADMIN_EMAIL)).first()
if not admin:
    db.add(User(organization_id=org.id, email=DEFAULT_ADMIN_EMAIL, hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD), role=Role.SUPER_ADMIN))
else:
    admin.email = DEFAULT_ADMIN_EMAIL
    admin.role = Role.SUPER_ADMIN
    admin.is_active = True
if admin and not verify_password(DEFAULT_ADMIN_PASSWORD, admin.hashed_password):
    admin.hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)
if not db.query(Member).first():
    member = Member(organization_id=org.id, member_id="SC-00001", first_name="Anita", last_name="Rao", mobile_number="+91-90000-00001", email="anita@example.com", date_of_birth=date(1952, 6, 10), city="Bengaluru")
    db.add(member); db.flush()
    db.add(Membership(member_id=member.id, membership_number="MEM-00001", membership_type="Annual", join_date=date.today(), expiry_date=date.today()+timedelta(days=365), status=MembershipStatus.ACTIVE))
if not db.query(Event).first():
    db.add(Event(organization_id=org.id, name="Wellness Workshop", venue="Community Hall", event_date=date.today()+timedelta(days=14), capacity=80, description="Healthy ageing session"))
if not db.query(Trip).first():
    db.add(Trip(organization_id=org.id, name="Mysuru Heritage Tour", destination="Mysuru", start_date=date.today()+timedelta(days=45), end_date=date.today()+timedelta(days=47), capacity=40, organizer="Travel Club", cost=7500))
for name in ["Walking Club", "Yoga Group", "Travel Club", "Reading Club", "Music Club"]:
    if not db.query(InterestGroup).filter_by(name=name).first(): db.add(InterestGroup(organization_id=org.id, name=name))
if not db.query(NotificationTemplate).first():
    db.add(NotificationTemplate(name="Membership Renewal Reminder", subject="Your membership renewal is due", body="Dear {{member}}, please renew your membership."))
db.commit(); db.close()
print("Seed data loaded")
