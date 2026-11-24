"""Row validation: airport list loading, single-row checks, record building."""

from datetime import datetime
import math
import re

FLIGHT_ID_RE = re.compile(r"^[A-Za-z0-9]{2,8}$")
AIRPORT_CODE_RE = re.compile(r"^[A-Z]{3}$")
DATETIME_SHAPE_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
DATETIME_FMT = "%Y-%m-%d %H:%M"

def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """

    airports: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if not code or code.startswith("#"):
                continue
            airports.add(code)
    return airports
    
def _parse_dt(text: str) -> datetime | None:
    """Validate YYYY-MM-DD HH:MM shape first, then parse real calendar date/time."""
    if not DATETIME_SHAPE_RE.fullmatch(text):
        return None
    try:
        return datetime.strptime(text, DATETIME_FMT)
    except ValueError:
        return None

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """

    # field count
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    # strip all fields before checking emptiness or field values
    cleaned = [field.strip() for field in fields]
    flight_id, origin, destination, dep_str, arr_str, price_str = cleaned

    # missing / whitespace-only field
    if any(value == "" for value in cleaned):
        return "MISSING_FIELD"

    # flight ID 
    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    # origin airport
    if not AIRPORT_CODE_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    # destination airport
    if not AIRPORT_CODE_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    # distinct origin and destination
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # departure datetime
    dep_dt = _parse_dt(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    # arrival datetime
    arr_dt = _parse_dt(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    # arrival strictly after departure
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # numeric and finite price
    try:
        price = float(price_str)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price):
        return "INVALID_PRICE"

    # strictly positive price
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    flight_id, origin, destination, dep_str, arr_str, price_str = [
        field.strip() for field in fields
    ]
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep_str,
        "arrival_datetime": arr_str,
        "price": float(price_str),
    }
