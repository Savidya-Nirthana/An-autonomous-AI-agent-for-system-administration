"""
Centralized path resolution for ChatOps.

Handles two runtime modes:
  1. Development  — paths resolve relative to the project root
  2. PyInstaller   — bundled data lives in sys._MEIPASS; user data in chosen location

The user picks an install location on first run. That location is persisted
in a small marker file at %APPDATA%/ChatOps/.install_path so we always know
where the user's data lives.
"""

import sys
import os
from pathlib import Path


def get_bundle_dir() -> Path:
    """Return the directory that holds bundled/read-only data files.

    In dev mode   → project root (where this file lives).
    As a frozen EXE → the temporary _MEIPASS directory PyInstaller extracts to.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def _default_data_dir() -> Path:
    """Fallback data directory before the user picks a location."""
    base = Path(os.environ.get("APPDATA", str(Path.home())))
    return base / "ChatOps"


def _marker_file() -> Path:
    """Small file in %APPDATA% that remembers the user-chosen install path."""
    base = Path(os.environ.get("APPDATA", str(Path.home())))
    marker_dir = base / "ChatOps"
    marker_dir.mkdir(parents=True, exist_ok=True)
    return marker_dir / ".install_path"


def get_user_data_dir() -> Path:
    """Return the user's chosen data directory.

    If the user has already run setup, reads the stored path from the marker.
    Otherwise returns the default (%APPDATA%/ChatOps).
    """
    marker = _marker_file()
    if marker.exists():
        stored = marker.read_text(encoding="utf-8").strip()
        if stored and Path(stored).exists():
            return Path(stored)
    return _default_data_dir()


def save_install_path(chosen_path: Path) -> None:
    """Persist the user's chosen install location to the marker file."""
    chosen_path.mkdir(parents=True, exist_ok=True)
    marker = _marker_file()
    marker.write_text(str(chosen_path), encoding="utf-8")


def is_first_run() -> bool:
    """Return True if the user has never completed setup."""
    marker = _marker_file()
    if not marker.exists():
        return True
    stored = marker.read_text(encoding="utf-8").strip()
    if not stored:
        return True
    data_dir = Path(stored)
    env_file = data_dir / ".env"
    return not env_file.exists()


# ── Convenience constants ─────────────────────────────────────────────
BUNDLE_DIR = get_bundle_dir()
USER_DATA_DIR = get_user_data_dir()
CONFIG_DIR = BUNDLE_DIR / "config"
ENV_FILE = USER_DATA_DIR / ".env"
QDRANT_DATA_DIR = USER_DATA_DIR / "qdrant_data"
EXECUTIONS_DIR = USER_DATA_DIR / "executions"
