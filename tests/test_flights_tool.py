from tools.get_flights import get_flights


def test_get_flights_round_trip():
    result = get_flights.invoke({
        "origin_iata": "AMD",
        "destination_iata": "GOI",
        "departure_date": "2026-09-01",
        "return_date": "2026-09-05"
    })

    print(result)

    assert "error" not in result
    assert result["origin"] == "AMD"
    assert result["destination"] == "GOI"
    assert result["departure_date"] == "2026-09-01"
    assert result["return_date"] == "2026-09-05"

    assert "offers" in result
    assert "return_offers" in result

    assert len(result["offers"]) > 0
    assert len(result["return_offers"]) > 0

    for flight in result["offers"]:
        assert flight["flight_number"] is not None
        assert flight["airline"] is not None
        assert flight["departure_airport"] == "AMD"
        assert flight["arrival_airport"] == "GOI"
        assert flight["departure"] is not None
        assert flight["arrival"] is not None
        assert flight["status"] is not None

    for flight in result["return_offers"]:
        assert flight["flight_number"] is not None
        assert flight["airline"] is not None
        assert flight["departure_airport"] == "GOI"
        assert flight["arrival_airport"] == "AMD"
        assert flight["departure"] is not None
        assert flight["arrival"] is not None
        assert flight["status"] is not None


def test_get_flights_one_way():
    result = get_flights.invoke({
        "origin_iata": "AMD",
        "destination_iata": "GOI",
        "departure_date": "2026-09-01"
    })

    print(result)

    assert "error" not in result
    assert result["origin"] == "AMD"
    assert result["destination"] == "GOI"
    assert result["departure_date"] == "2026-09-01"

    assert "offers" in result
    assert len(result["offers"]) > 0

    for flight in result["offers"]:
        assert flight["departure_airport"] == "AMD"
        assert flight["arrival_airport"] == "GOI"


def test_get_flights_invalid_airport_code():
    result = get_flights.invoke({
        "origin_iata": "AHMEDABAD",
        "destination_iata": "GOI",
        "departure_date": "2026-09-01"
    })

    assert "error" in result
    assert result["offers"] == []


def test_get_flights_invalid_date_format():
    result = get_flights.invoke({
        "origin_iata": "AMD",
        "destination_iata": "GOI",
        "departure_date": "1-09-2026"
    })

    assert "error" in result
    assert result["offers"] == []


def test_get_flights_return_date_before_departure():
    result = get_flights.invoke({
        "origin_iata": "AMD",
        "destination_iata": "GOI",
        "departure_date": "2026-09-05",
        "return_date": "2026-09-01"
    })

    assert "error" in result
    assert result["offers"] == []