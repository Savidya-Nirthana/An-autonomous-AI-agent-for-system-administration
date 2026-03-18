"""
=============================================================
  ROLE LIMITS CONFIGURATION — Edit this file to change limits
=============================================================
"""

# ── Allowed graph nodes (agents) per role ─────────────────────────────────────
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "root_admin": [
        "filesystem",
        "network",
        "firewall",
        "monitoring",
        "admin",
        "users",
        "servers",
        "system",
        "cmd",          # admin node — root_admin only
    ],
    "admin": [
        "filesystem",
        "network",
        "firewall",
        "monitoring",
        "users",
        "servers",
        "system",
        "cmd",
        ""
        # no "admin" node
    ],
    "user": [
        "filesystem",
        "network",
        "monitoring",
        "servers",
        # no "firewall" or "admin" node
    ],
}

# ── Per-role session & usage limits ───────────────────────────────────────────
ROLE_LIMITS: dict[str, dict] = {
    "root_admin": {
        "max_requests_per_session": -1,       # -1 = unlimited
        "max_sessions_per_day":     -1,
        "session_timeout_minutes":  480,       # 8 hours
        "max_prompt_length":        8000,
    },
    "admin": {
        "max_requests_per_session": 200,
        "max_sessions_per_day":     10,
        "session_timeout_minutes":  240,       # 4 hours
        "max_prompt_length":        4000,
    },
    "user": {
        "max_requests_per_session": 50,
        "max_sessions_per_day":     5,
        "session_timeout_minutes":  60,        # 1 hour
        "max_prompt_length":        2000,
    },
}
