"""
Address validation and sanitization utilities.

This module provides functions to validate and sanitize address inputs,
preventing security vulnerabilities and ensuring data quality.
"""

import re
from typing import Optional, Tuple
from html import escape

from app.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Exception raised for validation errors."""

    pass


def validate_address(address: Optional[str]) -> bool:
    """
    Validate an address string for basic format requirements.

    Args:
        address: Address string to validate

    Returns:
        True if address is valid, False otherwise
    """
    if not address:
        return False

    if not isinstance(address, str):
        return False

    # Remove leading/trailing whitespace
    address = address.strip()

    # Check minimum length
    if len(address) < 3:
        return False

    # Check maximum length (reasonable limit for addresses)
    if len(address) > 500:
        return False

    # Check for addresses that are too long without meaningful content (like just "AAAA...")
    if len(address) > 100 and len(set(address.lower())) < 5:
        return False

    # Check for suspicious patterns
    if _contains_malicious_content(address):
        return False

    # Check that it contains at least some alphanumeric characters AND meaningful content
    if not re.search(r"[a-zA-Z0-9]", address):
        return False

    # Check that it's not just numbers (like "123") - addresses need letters
    if re.match(r"^\d+$", address):
        return False

    # Address passes all validation checks
    return True


def sanitize_address(address: str) -> str:
    """
    Sanitize an address string by removing dangerous content.

    Args:
        address: Address string to sanitize

    Returns:
        Sanitized address string

    Raises:
        ValidationError: If address cannot be sanitized safely
    """
    if not address or not isinstance(address, str):
        raise ValidationError("Address must be a non-empty string")

    # Start with basic cleanup
    sanitized = address.strip()

    # Remove null bytes and control characters
    sanitized = "".join(
        char for char in sanitized if ord(char) >= 32 or char in "\t\n\r"
    )

    # Replace multiple whitespace with single spaces
    sanitized = re.sub(r"\s+", " ", sanitized)

    # Remove HTML tags
    sanitized = re.sub(r"<[^>]*>", "", sanitized)

    # Escape HTML entities
    sanitized = escape(sanitized)

    # Remove SQL injection patterns
    sanitized = _remove_sql_patterns(sanitized)

    # Remove script-like patterns
    sanitized = _remove_script_patterns(sanitized)

    # Final cleanup
    sanitized = sanitized.strip()

    # Validate the sanitized result
    if not sanitized or len(sanitized) < 3:
        raise ValidationError("Address becomes too short after sanitization")

    if len(sanitized) > 500:
        raise ValidationError("Address is too long even after sanitization")

    logger.debug(f"Sanitized address: '{address}' -> '{sanitized}'")
    return sanitized


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate latitude and longitude coordinates.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if coordinates are valid, False otherwise
    """
    try:
        # Check if values are already numeric types (not strings)
        if not isinstance(latitude, (int, float)) or not isinstance(
            longitude, (int, float)
        ):
            return False

        # Check if values are numeric
        lat = float(latitude)
        lng = float(longitude)

        # Check latitude bounds (-90 to 90)
        if lat < -90 or lat > 90:
            return False

        # Check longitude bounds (-180 to 180)
        if lng < -180 or lng > 180:
            return False

        # Check for NaN or infinity
        if not (abs(lat) < float("inf") and abs(lng) < float("inf")):
            return False

        # Check for NaN specifically
        if lat != lat or lng != lng:  # NaN != NaN is True
            return False

        return True

    except (ValueError, TypeError):
        return False


def normalize_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
    """
    Normalize coordinates to standard precision.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        Tuple of normalized (latitude, longitude)

    Raises:
        ValidationError: If coordinates are invalid
    """
    if not validate_coordinates(latitude, longitude):
        raise ValidationError(f"Invalid coordinates: {latitude}, {longitude}")

    # Round to 7 decimal places (roughly 1cm precision)
    normalized_lat = round(float(latitude), 7)
    normalized_lng = round(float(longitude), 7)

    return normalized_lat, normalized_lng


def _contains_malicious_content(text: str) -> bool:
    """
    Check if text contains potentially malicious content.

    Args:
        text: Text to check

    Returns:
        True if malicious content detected, False otherwise
    """
    # Convert to lowercase for case-insensitive matching
    lower_text = text.lower()

    # SQL injection patterns
    sql_patterns = [
        r"select\s+.*\s+from",
        r"insert\s+into",
        r"update\s+.*\s+set",
        r"delete\s+from",
        r"drop\s+table",
        r"union\s+select",
        r";\s*--",
        r";\s*/\*",
        r"\'\s*or\s+\d+\s*=\s*\d+",
        r"\'\s*or\s+\'\w+\'\s*=\s*\'\w+",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, lower_text):
            logger.warning(f"Detected SQL injection pattern: {pattern}")
            return True

    # XSS patterns
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"<iframe[^>]*>",
    ]

    for pattern in xss_patterns:
        if re.search(pattern, lower_text):
            logger.warning(f"Detected XSS pattern: {pattern}")
            return True

    return False


def _remove_sql_patterns(text: str) -> str:
    """
    Remove SQL injection patterns from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove common SQL keywords and patterns
    sql_removals = [
        r"select\s+.*\s+from.*",
        r"insert\s+into.*",
        r"update\s+.*\s+set.*",
        r"delete\s+from.*",
        r"drop\s+table.*",
        r"union\s+select.*",
        r";\s*--.*",
        r";\s*/\*.*?\*/",
        r"\'\s*or\s+.*",
        r"--.*",
        r"/\*.*?\*/",
    ]

    cleaned = text
    for pattern in sql_removals:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    return cleaned


def _remove_script_patterns(text: str) -> str:
    """
    Remove script-like patterns from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove script tags and event handlers
    script_removals = [
        r"<script[^>]*>.*?</script>",
        r'javascript:[^"\']*',
        r'on\w+\s*=\s*["\'][^"\']*["\']',
        r"<iframe[^>]*>.*?</iframe>",
    ]

    cleaned = text
    for pattern in script_removals:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    return cleaned


def validate_distance_unit(unit: str) -> bool:
    """
    Validate distance unit.

    Args:
        unit: Distance unit string

    Returns:
        True if unit is valid, False otherwise
    """
    valid_units = {"km", "kilometers", "mi", "miles", "meter", "meters", "m"}
    return unit.lower() in valid_units


def normalize_distance_unit(unit: str) -> str:
    """
    Normalize distance unit to standard form.

    Args:
        unit: Distance unit string

    Returns:
        Normalized unit string

    Raises:
        ValidationError: If unit is invalid
    """
    if not validate_distance_unit(unit):
        raise ValidationError(f"Invalid distance unit: {unit}")

    unit_lower = unit.lower()

    # Normalize to km or miles
    if unit_lower in {"km", "kilometers", "meter", "meters", "m"}:
        return "km"
    elif unit_lower in {"mi", "miles"}:
        return "miles"

    # Default to km
    return "km"


def validate_pagination_params(
    limit: Optional[int], offset: Optional[int]
) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.

    Args:
        limit: Number of items to return
        offset: Number of items to skip

    Returns:
        Tuple of validated (limit, offset)

    Raises:
        ValidationError: If parameters are invalid
    """
    # Validate limit
    if limit is None:
        limit = 10  # Default limit
    elif not isinstance(limit, int) or limit < 1:
        raise ValidationError("Limit must be a positive integer")
    elif limit > 100:
        raise ValidationError("Limit cannot exceed 100")

    # Validate offset
    if offset is None:
        offset = 0  # Default offset
    elif not isinstance(offset, int) or offset < 0:
        raise ValidationError("Offset must be a non-negative integer")
    elif offset > 10000:
        raise ValidationError("Offset cannot exceed 10000")

    return limit, offset
