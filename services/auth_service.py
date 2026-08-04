from __future__ import annotations

import re
from typing import Optional, Tuple

from flask_login import UserMixin

from database.mongo import create_user, get_user_by_email, get_user_by_id, serialize_user


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


class User(UserMixin):
    def __init__(self, user_doc: dict):
        self._user_doc = user_doc
        self.id = str(user_doc["_id"])
        self.name = user_doc.get("name", "")
        self.email = user_doc.get("email", "")

    @classmethod
    def from_id(cls, user_id: str) -> Optional["User"]:
        try:
            user = get_user_by_id(user_id)
        except RuntimeError:
            return None
        return cls(user) if user else None


def validate_email(email: str) -> Optional[str]:
    cleaned = email.strip().lower()
    if not EMAIL_PATTERN.match(cleaned):
        return "Enter a valid email address."
    try:
        if get_user_by_email(cleaned):
            return "An account with this email already exists."
    except RuntimeError as exc:
        return str(exc)
    return None


def validate_password(password: str) -> Optional[str]:
    if not PASSWORD_PATTERN.match(password):
        return "Password must be at least 8 characters and include uppercase, lowercase, and a number."
    return None


def hash_password(password: str) -> str:
    from extensions import bcrypt

    return bcrypt.generate_password_hash(password).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    from extensions import bcrypt

    return bcrypt.check_password_hash(password_hash, password)


def register_user(name: str, email: str, password: str) -> Tuple[bool, str]:
    name = name.strip()
    email = email.strip().lower()

    if not name:
        return False, "Name is required."

    email_error = validate_email(email)
    if email_error:
        return False, email_error

    password_error = validate_password(password)
    if password_error:
        return False, password_error

    try:
        create_user(name, email, hash_password(password))
    except RuntimeError as exc:
        return False, str(exc)
    return True, "Account created successfully."


def login_user(email: str, password: str):
    try:
        user = get_user_by_email(email.strip().lower())
    except RuntimeError:
        return None
    if not user:
        return None
    if not verify_password(password, user.get("password_hash", "")):
        return None
    return User(user)


def get_current_user_profile(user_id: str):
    try:
        return serialize_user(get_user_by_id(user_id))
    except RuntimeError:
        return None
