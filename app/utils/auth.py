import re
from werkzeug.security import generate_password_hash, check_password_hash


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Enforces application password complexity policy:
    - Minimum 8 characters
    - At least 1 letter
    - At least 1 number or special character
    Returns (is_valid, error_message).
    """
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter."
    if not re.search(r'[\d\W]', password):
        return False, "Password must contain at least one number or special character."
    return True, ""


def hash_password(password: str) -> str:
    """Generates a secure salted hash for a plain text password after validating strength."""
    is_valid, err = validate_password_strength(password)
    if not is_valid:
        raise ValueError(err)
    return generate_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored password hash."""
    if not plain_password or not hashed_password:
        return False
    return check_password_hash(hashed_password, plain_password)

