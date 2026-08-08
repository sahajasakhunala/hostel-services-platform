from datetime import datetime


def require_fields(data: dict, required_fields: list) -> dict:
    """
    Checks presence of required keys in request JSON payload.
    Returns dictionary of missing field errors.
    """
    errors = {}
    if not isinstance(data, dict):
        return {"payload": "Request payload must be a JSON object."}
    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
            errors[field] = f"'{field}' is a required field and cannot be empty."
    return errors


def validate_integer_id(val, field_name: str, allow_null=False) -> tuple[int | None, str | None]:
    """
    Validates that a field is a positive integer > 0.
    Returns (parsed_int, error_message).
    """
    if val is None:
        if allow_null:
            return None, None
        return None, f"'{field_name}' is required."
    try:
        # Check if float passed e.g. 1.5
        if isinstance(val, float) and not val.is_integer():
            return None, f"'{field_name}' must be a whole positive integer."
        int_val = int(val)
        if int_val <= 0:
            return None, f"'{field_name}' must be a positive integer greater than zero."
        return int_val, None
    except (ValueError, TypeError):
        return None, f"'{field_name}' must be a valid positive integer."


def validate_positive_amount(val, field_name: str = "amount") -> tuple[float | None, str | None]:
    """
    Validates that a numeric amount is positive (> 0) and non-nan.
    Returns (parsed_float, error_message).
    """
    if val is None:
        return None, f"'{field_name}' is required."
    try:
        float_val = float(val)
        if float_val <= 0:
            return None, f"'{field_name}' must be a numeric value greater than zero."
        return round(float_val, 2), None
    except (ValueError, TypeError):
        return None, f"'{field_name}' must be a valid numeric amount."


def validate_enum(val: str, allowed_values: list, field_name: str) -> tuple[str | None, str | None]:
    """
    Validates that a string value belongs to allowed enum choices.
    Returns (val, error_message).
    """
    if val is None:
        return None, f"'{field_name}' is required."
    val_str = str(val).strip()
    if val_str not in allowed_values:
        allowed_fmt = ", ".join([f"'{v}'" for v in allowed_values])
        return None, f"'{field_name}' must be one of: [{allowed_fmt}]."
    return val_str, None


def validate_date_string(val: str, field_name: str, format_str: str = "%Y-%m-%d") -> tuple[str | None, str | None]:
    """
    Validates format of date/datetime string.
    Returns (val_str, error_message).
    """
    if not val:
        return None, f"'{field_name}' is required."
    val_str = str(val).strip()
    try:
        datetime.strptime(val_str, format_str)
        return val_str, None
    except ValueError:
        return None, f"'{field_name}' must be a valid date string in format '{format_str}'."


def validate_string_length(val: str, field_name: str, max_length: int = 255, min_length: int = 1) -> tuple[str | None, str | None]:
    """
    Validates string length boundaries.
    Returns (val_str, error_message).
    """
    if val is None:
        return None, f"'{field_name}' is required."
    val_str = str(val).strip()
    if len(val_str) < min_length:
        return None, f"'{field_name}' must be at least {min_length} character(s) long."
    if len(val_str) > max_length:
        return None, f"'{field_name}' exceeds maximum length of {max_length} characters."
    return val_str, None


def parse_pagination_params(args, default_limit: int = 100, max_limit: int = 500) -> tuple[int, int, str | None]:
    """
    Parses and bounds limit and offset query parameters.
    Returns (limit, offset, error_message).
    """
    raw_limit = args.get('limit', default_limit)
    raw_offset = args.get('offset', 0)

    try:
        limit = int(raw_limit)
        if limit <= 0 or limit > max_limit:
            return default_limit, 0, f"'limit' parameter must be an integer between 1 and {max_limit}."
    except (ValueError, TypeError):
        return default_limit, 0, "'limit' parameter must be a valid integer."

    try:
        offset = int(raw_offset)
        if offset < 0:
            return default_limit, 0, "'offset' parameter must be a non-negative integer."
    except (ValueError, TypeError):
        return default_limit, 0, "'offset' parameter must be a valid non-negative integer."

    return limit, offset, None
