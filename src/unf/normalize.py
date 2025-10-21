"""Data normalization functions for UNF calculation.

This module implements the normalization rules for different data types
according to the UNF v6 specification.
"""

import math
from datetime import date, datetime, time
from decimal import Decimal, ROUND_HALF_EVEN
import base64


def normalize_numeric(
    value: float | int | None,
    precision: int = 7,
    round_mode: bool = True
) -> str:
    """Normalize a numeric value according to UNF v6 specification.

    Args:
        value: The numeric value to normalize. Can be None for missing values.
        precision: Number of significant digits (default 7).
        round_mode: If True, round to nearest (default). If False, truncate.

    Returns:
        Normalized string representation.

    Examples:
        >>> normalize_numeric(3.1415)
        '+3.141500e+00'
        >>> normalize_numeric(0.0)
        '+0.e+'
        >>> normalize_numeric(-0.0)
        '-0.e+'
        >>> normalize_numeric(float('inf'))
        '+inf'
        >>> normalize_numeric(None)
        '\\x00\\x00\\x00'
    """
    if value is None:
        return '\000\000\000'

    # Handle special float values
    if math.isnan(value):
        return '+nan'
    if math.isinf(value):
        return '+inf' if value > 0 else '-inf'

    # Handle zeros with sign preservation
    if value == 0.0:
        # Use copysign to detect -0.0
        if math.copysign(1.0, value) < 0:
            return '-0.e+'
        return '+0.e+'

    # Determine sign
    sign = '+' if value >= 0 else '-'
    abs_value = abs(value)

    # Convert to decimal for precise rounding
    decimal_value = Decimal(str(abs_value))

    # Calculate the exponent
    exponent = math.floor(math.log10(abs_value))

    # Scale to get significant digits
    scaled = decimal_value / Decimal(10 ** exponent)

    # Round or truncate to N significant digits
    if round_mode:
        # Round to N-1 decimal places (since we have 1 digit before decimal)
        factor = Decimal(10 ** (precision - 1))
        rounded = (scaled * factor).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN) / factor
    else:
        # Truncate
        factor = Decimal(10 ** (precision - 1))
        rounded = Decimal(int(scaled * factor)) / factor

    # Format the mantissa
    mantissa_str = f"{rounded:.{precision-1}f}"

    # Remove trailing zeros after decimal point
    if '.' in mantissa_str:
        mantissa_str = mantissa_str.rstrip('0').rstrip('.')
        if '.' not in mantissa_str:
            mantissa_str += '.'
    else:
        mantissa_str += '.'

    # Format exponent with sign
    exp_sign = '+' if exponent >= 0 else ''
    exp_str = f"{exp_sign}{exponent:02d}" if exponent != 0 else '+'

    return f"{sign}{mantissa_str}e{exp_str}"


def normalize_string(value: str | None, max_chars: int = 128) -> bytes:
    """Normalize a string value according to UNF v6 specification.

    Args:
        value: The string to normalize. Can be None for missing values.
        max_chars: Maximum number of characters to keep (default 128).

    Returns:
        UTF-8 encoded bytes (or b'\\x00\\x00\\x00' for None).
    """
    if value is None:
        return b'\000\000\000'

    # Truncate to max_chars characters
    truncated = value[:max_chars]

    # Encode as UTF-8
    return truncated.encode('utf-8')


def normalize_boolean(value: bool | None) -> str:
    """Normalize a boolean value as numeric (0 or 1).

    Args:
        value: The boolean value to normalize. Can be None for missing values.

    Returns:
        Normalized string representation.
    """
    if value is None:
        return '\000\000\000'

    return normalize_numeric(1 if value else 0)


def normalize_date(value: date | None) -> str:
    """Normalize a date value according to UNF v6 specification.

    Args:
        value: The date to normalize. Can be None for missing values.

    Returns:
        ISO 8601 formatted date string (YYYY-MM-DD).
    """
    if value is None:
        return '\000\000\000'

    return value.isoformat()


def normalize_time(value: time | None, timezone_aware: bool = True) -> str:
    """Normalize a time value according to UNF v6 specification.

    Args:
        value: The time to normalize. Can be None for missing values.
        timezone_aware: If True, convert to UTC and append 'Z'.

    Returns:
        ISO 8601 formatted time string.
    """
    if value is None:
        return '\000\000\000'

    # Format: hh:mm:ss.fffff with trailing zeros removed
    time_str = value.strftime('%H:%M:%S')

    # Add fractional seconds if present
    if value.microsecond > 0:
        fractional = f".{value.microsecond:06d}".rstrip('0')
        time_str += fractional

    # Append Z for UTC if timezone aware
    if timezone_aware:
        time_str += 'Z'

    return time_str


def normalize_datetime(value: datetime | None) -> str:
    """Normalize a datetime value according to UNF v6 specification.

    Args:
        value: The datetime to normalize. Can be None for missing values.

    Returns:
        ISO 8601 formatted datetime string (YYYY-MM-DDThh:mm:ss.fffffZ).
    """
    if value is None:
        return '\000\000\000'

    # Convert to UTC if timezone-aware
    if value.tzinfo is not None:
        value = value.astimezone(None).replace(tzinfo=None)

    date_part = normalize_date(value.date())
    time_part = normalize_time(value.time())

    return f"{date_part}T{time_part}"


def normalize_bitfield(bits: list[bool] | None) -> str:
    """Normalize a bitfield according to UNF v6 specification.

    Args:
        bits: List of boolean values representing bits. Can be None for missing values.

    Returns:
        Base64-encoded string of the bit field.
    """
    if bits is None or not bits:
        return '\000\000\000'

    # Remove leading False values
    while bits and not bits[0]:
        bits = bits[1:]

    if not bits:
        return '\000\000\000'

    # Convert bits to bytes (big-endian)
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_val = 0
        for j in range(8):
            if i + j < len(bits) and bits[i + j]:
                byte_val |= (1 << (7 - j))
        byte_array.append(byte_val)

    # Base64 encode
    return base64.b64encode(bytes(byte_array)).decode('ascii')
