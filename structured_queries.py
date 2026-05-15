import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple


ContentRow = Dict[str, Any]
StructuredResponse = Tuple[str, List[Dict[str, Any]]]


CATEGORY_ALIASES = {
    "church": {"church", "churches"},
    "churches": {"church", "churches"},
    "temple": {"temple", "temples", "hindu deities", "hindu deity"},
    "temples": {"temple", "temples", "hindu deities", "hindu deity"},
}


GOA_PLACE_COORDINATES = {
    "panaji": (15.4909, 73.8278),
    "panjim": (15.4909, 73.8278),
    "margao": (15.2832, 73.9862),
    "madgaon": (15.2832, 73.9862),
    "vasco": (15.3860, 73.8440),
    "vasco da gama": (15.3860, 73.8440),
    "mapusa": (15.5915, 73.8089),
    "ponda": (15.4034, 74.0152),
    "old goa": (15.5007, 73.9116),
    "calangute": (15.5439, 73.7553),
    "candolim": (15.5184, 73.7626),
    "colva": (15.2798, 73.9228),
    "benaulim": (15.2645, 73.9289),
    "assolna": (15.1801, 73.9709),
    "chandor": (15.2635, 74.0473),
    "valpoi": (15.5324, 74.1367),
}


LIST_VERBS = {
    "list",
    "show",
    "display",
    "give",
    "tell",
    "which",
}


def normalize_text(text: Any) -> str:
    lowered = str(text or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def normalize_category(text: Any) -> str:
    return normalize_text(text)


def parse_category_list_request(query: str) -> Optional[Tuple[str, set[str]]]:
    query_norm = normalize_text(query)
    if not query_norm:
        return None

    tokens = set(query_norm.split())
    has_list_intent = bool(tokens & LIST_VERBS) or bool(
        re.search(r"\ball\s+(?:the\s+)?(?:churches|church|temples|temple)\b", query_norm)
    )

    if not has_list_intent:
        return None

    for label, aliases in CATEGORY_ALIASES.items():
        if any(re.search(rf"\b{re.escape(alias)}\b", query_norm) for alias in aliases):
            display_label = "temples" if label.startswith("temple") else "churches"
            return display_label, aliases

    return None


def row_matches_category(row: ContentRow, aliases: Iterable[str]) -> bool:
    category = normalize_category(row.get("category"))
    if not category:
        return False

    return any(category == normalize_category(alias) for alias in aliases)


def source_from_row(row: ContentRow) -> Dict[str, Any]:
    return {
        "content_id": str(row.get("id", "")),
        "title": stringify(row.get("title")),
        "category": stringify(row.get("category")),
        "source": "supabase",
    }


def stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def row_title(row: ContentRow) -> str:
    return stringify(row.get("title") or row.get("name") or "Untitled location")


def row_description(row: ContentRow) -> str:
    return stringify(
        row.get("shortDescription")
        or row.get("description")
        or row.get("longDescription")
    )


def format_category_list_response(
    label: str,
    rows: Iterable[ContentRow],
    aliases: Iterable[str],
) -> StructuredResponse:
    matches = [
        row
        for row in rows
        if row_matches_category(row, aliases)
    ]
    matches.sort(key=lambda item: row_title(item).lower())

    if not matches:
        return (
            f"No {label} found in the knowledge base.",
            [],
        )

    count = len(matches)
    display_label = singular_label(label) if count == 1 else label
    lines = [f"I found {count} {display_label} in the knowledge base:"]
    for index, row in enumerate(matches, start=1):
        title = row_title(row)
        category = stringify(row.get("category"))
        description = row_description(row)
        location = format_coordinates(row)

        details = []
        if category:
            details.append(category)
        if location:
            details.append(location)

        suffix = f" ({'; '.join(details)})" if details else ""
        summary = f" - {description}" if description else ""
        lines.append(f"{index}. {title}{suffix}{summary}")

    return "\n".join(lines), [source_from_row(row) for row in matches]


def singular_label(label: str) -> str:
    labels = {
        "churches": "church",
        "temples": "temple",
    }
    return labels.get(label, label.rstrip("s"))


def format_coordinates(row: ContentRow) -> str:
    latitude = parse_float(row.get("latitude"))
    longitude = parse_float(row.get("longitude"))
    if latitude is None or longitude is None:
        return ""
    return f"{latitude:.4f}, {longitude:.4f}"


def parse_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_distance_request(query: str) -> Optional[Tuple[str, str]]:
    cleaned = query.strip().rstrip("?!.")
    patterns = [
        r"\b(?:distance|how far).*?\bfrom\s+(.+?)\s+\bto\s+(.+)$",
        r"\b(?:distance|how far).*?\bbetween\s+(.+?)\s+\band\s+(.+)$",
        r"\bhow far\s+(?:is|are)\s+(.+?)\s+\bfrom\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return clean_place_phrase(match.group(1)), clean_place_phrase(match.group(2))

    return None


def clean_place_phrase(phrase: str) -> str:
    cleaned = re.sub(
        r"\b(?:in|inside|within|goa|the|a|an|location|place|site)\b",
        " ",
        phrase,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", cleaned).strip(" ,")


def haversine_km(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> float:
    earth_radius_km = 6371.0088
    origin_latitude_rad = math.radians(origin_latitude)
    destination_latitude_rad = math.radians(destination_latitude)
    delta_latitude = math.radians(destination_latitude - origin_latitude)
    delta_longitude = math.radians(destination_longitude - origin_longitude)

    a = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(origin_latitude_rad)
        * math.cos(destination_latitude_rad)
        * math.sin(delta_longitude / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_km * c


def resolve_location(name: str, rows: Iterable[ContentRow]) -> Optional[Dict[str, Any]]:
    normalized_name = normalize_text(name)
    if not normalized_name:
        return None

    gazetteer_coordinates = GOA_PLACE_COORDINATES.get(normalized_name)
    if gazetteer_coordinates:
        latitude, longitude = gazetteer_coordinates
        canonical_name = canonical_place_name(normalized_name)
        return {
            "name": canonical_name,
            "latitude": latitude,
            "longitude": longitude,
            "source": {"title": canonical_name, "source": "gazetteer"},
        }

    candidates = []
    query_tokens = set(normalized_name.split())

    for row in rows:
        latitude = parse_float(row.get("latitude"))
        longitude = parse_float(row.get("longitude"))
        if latitude is None or longitude is None:
            continue

        title = row_title(row)
        normalized_title = normalize_text(title)
        title_tokens = set(normalized_title.split())
        if not normalized_title:
            continue

        score = 0.0
        if normalized_name == normalized_title:
            score += 100.0
        if normalized_name in normalized_title or normalized_title in normalized_name:
            score += 50.0
        if query_tokens:
            token_hits = len(query_tokens & title_tokens)
            score += token_hits * 10.0
            if token_hits == len(query_tokens):
                score += 20.0

        if score > 0:
            candidates.append((score, title, latitude, longitude, row))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (-item[0], item[1].lower()))
    _, title, latitude, longitude, row = candidates[0]
    return {
        "name": title,
        "latitude": latitude,
        "longitude": longitude,
        "source": source_from_row(row),
    }


def canonical_place_name(normalized_name: str) -> str:
    names = {
        "panaji": "Panaji",
        "panjim": "Panaji",
        "margao": "Margao",
        "madgaon": "Margao",
        "vasco": "Vasco da Gama",
        "vasco da gama": "Vasco da Gama",
        "mapusa": "Mapusa",
        "ponda": "Ponda",
        "old goa": "Old Goa",
        "calangute": "Calangute",
        "candolim": "Candolim",
        "colva": "Colva",
        "benaulim": "Benaulim",
        "assolna": "Assolna",
        "chandor": "Chandor",
        "valpoi": "Valpoi",
    }
    return names.get(normalized_name, normalized_name.title())


def format_distance_response(query: str, rows: Iterable[ContentRow]) -> Optional[StructuredResponse]:
    parsed = parse_distance_request(query)
    if not parsed:
        return None

    origin_name, destination_name = parsed
    row_list = list(rows)
    origin = resolve_location(origin_name, row_list)
    destination = resolve_location(destination_name, row_list)

    if origin is None or destination is None:
        missing = []
        if origin is None:
            missing.append(origin_name)
        if destination is None:
            missing.append(destination_name)

        return (
            "I could not calculate the distance because I could not resolve "
            f"{', '.join(missing)} to Goa locations with coordinates.",
            [],
        )

    distance_km = haversine_km(
        origin["latitude"],
        origin["longitude"],
        destination["latitude"],
        destination["longitude"],
    )
    response = (
        f"The approximate straight-line distance from {origin['name']} to "
        f"{destination['name']} is {distance_km:.1f} km."
    )

    sources = []
    for location in (origin, destination):
        source = location.get("source")
        if source and source not in sources:
            sources.append(source)

    return response, sources


def build_structured_query_response(
    query: str,
    rows: Iterable[ContentRow],
) -> Optional[StructuredResponse]:
    row_list = list(rows)

    distance_response = format_distance_response(query, row_list)
    if distance_response:
        return distance_response

    category_request = parse_category_list_request(query)
    if category_request:
        label, aliases = category_request
        return format_category_list_response(label, row_list, aliases)

    return None
