from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Attendance, Event, EventRegistration, Member, Membership, MembershipStatus, Trip

def get_dashboard(db: Session):
    today = date.today()
    month = today.month
    total_members = db.query(Member).count()
    active_members = db.query(Membership).filter(Membership.status == MembershipStatus.ACTIVE).count()
    expired = db.query(Membership).filter(Membership.status == MembershipStatus.EXPIRED).count()
    renewals_due = db.query(Membership).filter(Membership.expiry_date <= today + timedelta(days=30)).count()
    upcoming_events = db.query(Event).filter(Event.event_date >= today).count()
    registrations = db.query(EventRegistration).count()
    attended = db.query(Attendance).filter(Attendance.attended.is_(True)).count()
    upcoming_trips = db.query(Trip).filter(Trip.start_date >= today).count()
    birthdays = db.query(Member).filter(func.strftime('%m', Member.date_of_birth) == f"{month:02d}").count()
    return {
        "total_members": total_members,
        "active_members": active_members,
        "expired_memberships": expired,
        "renewals_due": renewals_due,
        "upcoming_events": upcoming_events,
        "event_registrations": registrations,
        "attendance_rate": round((attended / registrations) * 100, 2) if registrations else 0,
        "upcoming_trips": upcoming_trips,
        "birthdays_this_month": birthdays,
    }
