"""
Core authentication & authorisation business logic.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

import bcrypt
from sqlalchemy.orm import Session as DBSession

from auth.models import AuditLog, Session, User, UserRole, get_db
from config.role_limits import ROLE_LIMITS, ROLE_PERMISSIONS


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── Auth Service ──────────────────────────────────────────────────────────────

class AuthService:
    """Handles login, session management, user CRUD, and permission checks."""

    # ── Login / Logout ────────────────────────────────────────────────────────

    def login(
        self, username: str, password: str, db: DBSession
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Validate credentials and create a session.
        Returns (session_id, error_message).
        """
        user = db.query(User).filter_by(username=username, is_active=True).first()
        if not user or not verify_password(password, user.password_hash):
            self._audit(db, None, None, "LOGIN_FAILED",
                        f"Failed login attempt for username={username!r}")
            return None, "Invalid username or password."

        limits = ROLE_LIMITS[user.role.value]

        # Check daily session cap (skip for unlimited roles)
        max_daily = limits["max_sessions_per_day"]
        if max_daily != -1:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
            daily_count = (
                db.query(Session)
                .filter(
                    Session.user_id == user.id,
                    Session.created_at >= today_start,
                )
                .count()
            )
            if daily_count >= max_daily:
                return None, (
                    f"Daily session limit reached ({max_daily}/day). "
                    "Try again tomorrow."
                )

        # Build session
        session_id = f"{username}-{uuid.uuid4().hex[:8]}"
        expires_at = datetime.utcnow() + timedelta(
            minutes=limits["session_timeout_minutes"]
        )
        new_session = Session(
            session_id=session_id,
            user_id=user.id,
            expires_at=expires_at,
        )
        user.last_login = datetime.utcnow()
        db.add(new_session)
        db.commit()

        self._audit(db, user.id, session_id, "LOGIN_SUCCESS", f"role={user.role.value}")
        return session_id, None

    def logout(self, session_id: str, db: DBSession) -> None:
        sess = db.query(Session).filter_by(session_id=session_id).first()
        if sess:
            sess.is_active = False
            db.commit()
            self._audit(db, sess.user_id, session_id, "LOGOUT", "")

    # ── Session validation ────────────────────────────────────────────────────

    def validate_session(
        self, session_id: str, db: DBSession
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Check that a session is still valid.
        Returns (User, error_message).
        """
        sess = (
            db.query(Session)
            .filter_by(session_id=session_id, is_active=True)
            .first()
        )
        if not sess:
            return None, "Session not found or already expired."
        if datetime.utcnow() > sess.expires_at:
            sess.is_active = False
            db.commit()
            return None, "Session has expired. Please log in again."

        user = db.query(User).filter_by(id=sess.user_id, is_active=True).first()
        if not user:
            return None, "User account is disabled."

        limits = ROLE_LIMITS[user.role.value]
        max_req = limits["max_requests_per_session"]
        if max_req != -1 and sess.request_count >= max_req:
            return None, (
                f"Request limit reached ({max_req} requests/session). "
                "Please start a new session."
            )

        return user, None

    def increment_request_count(self, session_id: str, db: DBSession) -> None:
        sess = db.query(Session).filter_by(session_id=session_id).first()
        if sess:
            sess.request_count += 1
            db.commit()

    # ── Permission checks ─────────────────────────────────────────────────────

    def can_use_tool(self, user: User, tool_name: str) -> bool:
        allowed = ROLE_PERMISSIONS.get(user.role.value, [])
        return tool_name in allowed

    def get_prompt_limit(self, user: User) -> int:
        return ROLE_LIMITS[user.role.value]["max_prompt_length"]

    # ── User management (root_admin only) ─────────────────────────────────────

    def create_user(
        self,
        actor: User,
        username: str,
        password: str,
        role: str,
        db: DBSession,
    ) -> Tuple[Optional[User], Optional[str]]:
        """Only root_admin may create users."""
        if actor.role != UserRole.root_admin:
            return None, "Permission denied: only root_admin can create users."

        if role not in ("admin", "user"):
            return None, "Invalid role. Choose 'admin' or 'user'."

        existing = db.query(User).filter_by(username=username).first()
        if existing:
            return None, f"Username {username!r} already exists."

        new_user = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole[role],
            created_by=actor.id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        self._audit(
            db, actor.id, None, "CREATE_USER",
            f"created username={username!r} role={role}",
        )
        return new_user, None

    def deactivate_user(
        self, actor: User, username: str, db: DBSession
    ) -> Tuple[bool, Optional[str]]:
        if actor.role != UserRole.root_admin:
            return False, "Permission denied: only root_admin can deactivate users."

        target = db.query(User).filter_by(username=username).first()
        if not target:
            return False, f"User {username!r} not found."
        if target.role == UserRole.root_admin:
            return False, "Cannot deactivate another root_admin."

        target.is_active = False
        # Invalidate all active sessions
        db.query(Session).filter_by(user_id=target.id, is_active=True).update(
            {"is_active": False}
        )
        db.commit()
        self._audit(db, actor.id, None, "DEACTIVATE_USER", f"username={username!r}")
        return True, None

    def list_users(self, actor: User, db: DBSession):
        """Root admin sees everyone; others cannot call this."""
        if actor.role != UserRole.root_admin:
            return []
        return db.query(User).order_by(User.id).all()

    def reset_password(
        self, actor: User, username: str, new_password: str, db: DBSession
    ) -> Tuple[bool, Optional[str]]:
        if actor.role != UserRole.root_admin:
            return False, "Permission denied."
        target = db.query(User).filter_by(username=username).first()
        if not target:
            return False, f"User {username!r} not found."
        target.password_hash = hash_password(new_password)
        db.commit()
        self._audit(db, actor.id, None, "RESET_PASSWORD", f"username={username!r}")
        return True, None

    # ── Audit helper ──────────────────────────────────────────────────────────

    def _audit(
        self,
        db: DBSession,
        user_id: Optional[int],
        session_id: Optional[str],
        action: str,
        details: str,
    ) -> None:
        try:
            log = AuditLog(
                user_id=user_id or 0,
                session_id=session_id,
                action=action,
                details=details,
            )
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()


# ── Singleton ─────────────────────────────────────────────────────────────────
auth_service = AuthService()
