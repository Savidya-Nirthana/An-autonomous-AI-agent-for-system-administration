#!/usr/bin/env python
"""
Bootstrap the database with a root_admin account.

Run once after `docker compose up`:
    python -m auth.seed

Set ROOT_ADMIN_USERNAME / ROOT_ADMIN_PASSWORD env vars (or .env) to
override the defaults before running in production.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def seed() -> None:
    # Import here so the module works standalone
    from auth.models import SessionLocal, User, UserRole, init_db
    from auth.auth_service import hash_password

    init_db()  # ensure tables exist

    username = os.getenv("ROOT_ADMIN_USERNAME", "root_admin")
    password = os.getenv("ROOT_ADMIN_PASSWORD", "ChangeMe123!")

    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            print(f"[seed] root_admin '{username}' already exists — skipping.")
            return

        root = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.root_admin,
            is_active=True,
        )
        db.add(root)
        db.commit()
        print(f"[seed] Created root_admin '{username}'.")
        print("[seed] ⚠️  Change the default password immediately!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
