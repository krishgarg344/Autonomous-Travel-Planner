import requests
from langchain_core.tools import tool
from config import AERODATA_API_KEY

BASE_URL = "https://aerodatabox.p.rapidapi.com"


def _fetch_departures(airport, date, headers):
    url = f"{BASE_URL}/flights/airports/iata/{airport}/{date}T00:00/{date}T23:59"
    params = {
        "direction": "Departure",
        "withLeg": "true",
        "withCancelled": "false",
        "withCargo": "false",
        "withPrivate": "false",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("departures", []) or []


def _to_offer(flight, expected_destination):
    arrival = flight.get("arrival") or {}
    arrival_airport = arrival.get("airport") or {}

    if (arrival_airport.get("iata") or "").upper() != expected_destination:
        return None

    departure = flight.get("departure") or {}
    airline = flight.get("airline") or {}

    return {
        "flight_number": flight.get("number"),
        "airline": airline.get("name"),
        "carrier": airline.get("iata"),
        "departure_airport": (departure.get("airport") or {}).get("iata"),
        "arrival_airport": arrival_airport.get("iata"),
        "departure": (departure.get("scheduledTime") or {}).get("local"),
        "arrival": (arrival.get("scheduledTime") or {}).get("local"),
        "status": flight.get("status"),
    }


def _search_offers(origin, destination, date, headers):
    flights = _fetch_departures(origin, date, headers)
    offers = [_to_offer(f, destination) for f in flights]
    return [o for o in offers if o][:10]


@tool
def get_flights(
    origin_iata: str,
    destination_iata: str,
    departure_date: str,
    return_date: str = None
) -> dict:
    """Search flights between two airports on a specific date.

    origin_iata and destination_iata must be 3-letter IATA airport codes,
    e.g. AMD and GOI.

    departure_date and return_date must be YYYY-MM-DD.
    Returns up to 10 matching flights.
    """
    if not AERODATA_API_KEY:
        return {"error": "AERODATA_API_KEY not configured. Add it to .env.", "offers": []}

    origin_iata = origin_iata.strip().upper()
    destination_iata = destination_iata.strip().upper()

    if len(origin_iata) != 3 or len(destination_iata) != 3:
        return {"error": "Origin and destination must be 3-letter IATA airport codes.", "offers": []}

    from datetime import datetime

    try:
        departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")

        if return_date:
            return_dt = datetime.strptime(return_date, "%Y-%m-%d")

            if return_dt < departure_dt:
                return {
                    "error": "Return date cannot be before departure date.",
                    "offers": []
                }

    except ValueError:
        return {
            "error": "Dates must be in YYYY-MM-DD format.",
            "offers": []
        }

    headers = {
        "Accept": "application/json",
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
        "X-RapidAPI-Key": AERODATA_API_KEY,
    }

    try:
        result = {
            "origin": origin_iata,
            "destination": destination_iata,
            "departure_date": departure_date,
            "offers": _search_offers(origin_iata, destination_iata, departure_date, headers),
        }

        if return_date:
            result["return_date"] = return_date
            result["return_offers"] = _search_offers(destination_iata, origin_iata, return_date, headers)

        return result

    except Exception as e:
        return {"error": str(e), "offers": []}