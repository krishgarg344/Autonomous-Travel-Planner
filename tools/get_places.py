import requests
from langchain_core.tools import tool
from config import GOOGLE_MAPS_API_KEY


@tool
def get_places(city: str, interests: str = "") -> dict:
    """Find attractions, restaurants, or stays in a city matching the given interests.
    Returns name, rating, price level, and address for each result.
    """

    if not GOOGLE_MAPS_API_KEY:
        return {
            "error": "GOOGLE_MAPS_API_KEY not configured. Add it to .env.",
            "places": []
        }

    try:
        query = (
            f"{interests} in {city}"
            if interests
            else f"popular attractions in {city}"
        )

        resp = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": (
                    "places.displayName,"
                    "places.formattedAddress,"
                    "places.rating,"
                    "places.priceLevel"
                ),
            },
            json={
                "textQuery": query
            },
            timeout=10,
        )

        resp.raise_for_status()

        data = resp.json()

        places = []

        for r in data.get("places", [])[:10]:
            places.append({
                "name": r.get("displayName", {}).get("text"),
                "address": r.get("formattedAddress"),
                "rating": r.get("rating"),
                "price_level": r.get("priceLevel"),
            })

        return {
            "city": city,
            "places": places
        }

    except Exception as e:
        return {
            "error": str(e),
            "places": []
        }