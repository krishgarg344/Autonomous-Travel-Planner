from tools.get_places import get_places


def test_get_places_with_interests():
    result = get_places.invoke({
        "city": "Jaipur",
        "interests": "historical places"
    })

    print(result)

    assert "places" in result
    assert "error" not in result
    assert len(result["places"]) > 0

    for place in result["places"]:
        assert "name" in place
        assert "address" in place
        assert "rating" in place
        assert "price_level" in place


def test_get_places_without_interests():
    result = get_places.invoke({
        "city": "Jaipur"
    })

    print(result)

    assert "places" in result
    assert "error" not in result
    assert len(result["places"]) > 0

    for place in result["places"]:
        assert "name" in place
        assert "address" in place
        assert "rating" in place
        assert "price_level" in place