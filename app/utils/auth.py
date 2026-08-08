from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Generates a secure salted hash for a plain text password."""
    return generate_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored password hash."""
    return check_password_hash(hashed_password, plain_password)
