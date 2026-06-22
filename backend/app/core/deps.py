from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import get_db
from app.models import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

PAGE_PREFIXES = {
    "dashboard": ("/dashboard",),
    "members": ("/members", "/documents"),
    "memberships": ("/memberships",),
    "membership-types": ("/membership-types",),
    "events": ("/events",),
    "trips": ("/trips",),
    "community": ("/announcements", "/groups"),
    "notifications": ("/notifications",),
    "payments": ("/payments",),
    "reports": ("/reports",),
    "users": ("/users", "/auth/me"),
}

def _page_for_path(path: str) -> str | None:
    api_path = path[4:] if path.startswith("/api/") else path
    for page, prefixes in PAGE_PREFIXES.items():
        if any(api_path.startswith(prefix) for prefix in prefixes):
            return page
    return None

def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role != Role.SUPER_ADMIN:
        page = _page_for_path(request.url.path)
        allowed = set(filter(None, (user.allowed_pages or "").split(",")))
        if page and allowed and page not in allowed:
            raise HTTPException(status_code=403, detail="Page access denied")
    return user

def require_roles(*roles: Role):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles and user.role != Role.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker
