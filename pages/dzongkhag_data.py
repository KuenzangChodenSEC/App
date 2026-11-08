from .database import get_places
from .places_data import slugify

# Coordinates are used for manual location selection and distance recommendations.
_DZONGKHAG_COORDS = {
    "Haa": (27.3875, 89.2807),
    "Paro": (27.4305, 89.4120),
    "Punakha": (27.5926, 89.8770),
    "Samtse": (26.8990, 89.0990),
    "Tashi Yangtse": (27.6110, 91.4980),
    "Thimphu": (27.4728, 89.6390),
}

DZONGKHAGS = [
    {"name": name, "tagline": f"Explore places in {name}", "region": name,
     "town": name, "description": f"Discover the destinations and attractions of {name}, Bhutan.",
     "best": "Varies by season", "climate": "Climate varies depending on altitude and season.",
     "lat": coords[0], "lon": coords[1]}
    for name, coords in _DZONGKHAG_COORDS.items()
]

def dzongkhag_by_name(name):
    """Return the dzongkhag record matching a name, ignoring case and spacing."""
    if not name:
        return None
    key = str(name).strip().lower()
    for dz in DZONGKHAGS:
        if dz["name"].lower() == key:
            return dz
    return None

def places_in(dzongkhag):
    name = dzongkhag["name"] if isinstance(dzongkhag, dict) else dzongkhag
    return get_places(district=name)

def dzongkhag_rating(dzongkhag):
    ps = places_in(dzongkhag)
    if not ps:
        return 0.0, 0, 0
    ratings = [float(p.get("rating", 0) or 0) for p in ps]
    rated = [r for r in ratings if r > 0]
    average = sum(rated) / len(rated) if rated else 0.0
    reviews = sum(int(p.get("reviews", 0) or 0) for p in ps)
    return round(average, 1), reviews, len(ps)

def dzongkhag_of_place(place):
    """Return the full dzongkhag record for a place (needed by recommendations)."""
    district = place.get("district") or place.get("location", "")
    return dzongkhag_by_name(district)

__all__ = ["DZONGKHAGS", "dzongkhag_by_name", "dzongkhag_rating",
           "places_in", "dzongkhag_of_place", "slugify"]
