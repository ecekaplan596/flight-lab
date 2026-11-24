"""Running queries against the flight database."""
import math

from validator import _parse_dt

RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

ALLOWED_KEYS = RECORD_KEYS | {
    "min_price",
    "sort_by",
    "order",
    "limit",
}

def _is_valid_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _validate_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    if any(key not in ALLOWED_KEYS for key in query):
        return False

    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            val = query[key]
            if not isinstance(val, str) or _parse_dt(val) is None:
                return False

    for key in ("price", "min_price"):
        if key in query and not _is_valid_number(query[key]):
            return False

    if "sort_by" in query:
        sort_by = query["sort_by"]
        if not isinstance(sort_by, str) or sort_by not in RECORD_KEYS:
            return False

    if "order" in query:
        if "sort_by" not in query:
            return False
        if query["order"] not in ("asc", "desc"):
            return False

    if "limit" in query:
        limit = query["limit"]
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            return False

    return True


def _matches_record(record: dict, query: dict) -> bool:
    if "flight_id" in query and record["flight_id"] != query["flight_id"]:
        return False
    if "origin" in query and record["origin"] != query["origin"]:
        return False
    if "destination" in query and record["destination"] != query["destination"]:
        return False
    if (
        "departure_datetime" in query
        and record["departure_datetime"] < query["departure_datetime"]
    ):
        return False
    if (
        "arrival_datetime" in query
        and record["arrival_datetime"] > query["arrival_datetime"]
    ):
        return False
    if "price" in query and record["price"] > query["price"]:
        return False
    if "min_price" in query and record["price"] < query["min_price"]:
        return False
    return True

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _validate_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [record for record in db if _matches_record(record, query)]

    if "sort_by" in query:
        sort_by = query["sort_by"]
        order = query.get("order", "asc")
        matches = sorted(
            matches,
            key=lambda record: record[sort_by],
            reverse=(order == "desc"),
        )

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    query_list = [queries] if isinstance(queries, dict) else queries
    return [run_query(db, q) for q in query_list]
