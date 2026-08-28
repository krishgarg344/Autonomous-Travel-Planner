import schemas
from pydantic import ValidationError
from schemas import TripRequest, Itinerary, DayPlan, Activity


def run_repl_tests():
    print("==================================================")
    print("1. TEST: Valid TripRequest Unpacking")
    print("==================================================")
    valid_sample_dict = {
        "origin_city": "Mumbai",
        "destination_city": "Goa",
        "start_date": "2026-10-15",
        "end_date": "2026-10-18",
        "total_budget": 35000.0,
        "interests": "beaches, food, nightlife",
        "travelers": 2
    }

    try:
        request_obj = TripRequest(**valid_sample_dict)
        print("✅ TripRequest instantiated successfully:")
        print(f"   Origin: {request_obj.origin_city}")
        print(f"   Destination: {request_obj.destination_city}")
        print(f"   Budget: ₹{request_obj.total_budget:,.2f}")
        print(f"   Travelers: {request_obj.travelers}")
    except ValidationError as e:
        print("❌ Unexpected Validation Error:", e)

    print("\n==================================================")
    print("2. TEST: TripRequest Defaults (Missing Optional Field)")
    print("==================================================")
    # Testing that 'travelers' defaults to 1 when omitted from dict
    minimal_sample_dict = {
        "origin_city": "Delhi",
        "destination_city": "Jaipur",
        "start_date": "2026-11-01",
        "end_date": "2026-11-03",
        "total_budget": 15000.0,
        "interests": "forts, local crafts"
    }

    request_minimal = TripRequest(**minimal_sample_dict)
    print(f"✅ Default travelers count: {request_minimal.travelers} (Expected: 1)")

    print("\n==================================================")
    print("3. TEST: TripRequest Validation Failures")
    print("==================================================")
    invalid_sample_dict = {
        "origin_city": "Bengaluru",
        "destination_city": "Kochi",
        "start_date": "2026-12-01",
        # "end_date" is missing!
        "total_budget": "not_a_number", # Invalid float type!
        "interests": "backwaters"
    }

    try:
        TripRequest(**invalid_sample_dict)
    except ValidationError as e:
        print("✅ Successfully caught expected validation errors:")
        for error in e.errors():
            print(f"   - Field '{error['loc'][0]}': {error['msg']}")

    print("\n==================================================")
    print("4. TEST: Nested Itinerary Output Construction")
    print("==================================================")
    itinerary_sample_dict = {
        "destination_city": "Goa",
        "start_date": "2026-10-15",
        "end_date": "2026-10-16",
        "flight_cost": 8000.0,
        "total_cost": 14500.0,
        "total_budget": 35000.0,
        "days": [
            {
                "date": "2026-10-15",
                "weather_summary": "Sunny, 29°C",
                "activities": [
                    {
                        "time_of_day": "afternoon",
                        "name": "Baga Beach Relaxation",
                        "description": "Unwind at local beach shacks",
                        "cost": 1500.0
                    },
                    {
                        "time_of_day": "evening",
                        "name": "Seafood Dinner",
                        "description": "Dine at Fisherman's Wharf",
                        "cost": 3500.0
                    }
                ],
                "day_total_cost": 5000.0
            }
        ],
        "notes": "Well within total budget allowance."
    }

    itinerary_obj = Itinerary(**itinerary_sample_dict)
    print("✅ Nested Itinerary parsed successfully!")
    print(f"   Total Days: {len(itinerary_obj.days)}")
    print(f"   Day 1 Activity 1: {itinerary_obj.days[0].activities[0].name} (₹{itinerary_obj.days[0].activities[0].cost})")


def test_activity_and_dayplan():
    print("==================================================")
    print("1. TEST: Individual Activity Validation")
    print("==================================================")
    activity_dict = {
        "time_of_day": "morning",
        "name": "Visit Amber Fort",
        "description": "Explore the historic palace fort in Jaipur",
        "cost": 500.0,
    }

    try:
        act = Activity(**activity_dict)
        print("✅ Activity instantiated successfully:")
        print(f"   Name: {act.name}")
        print(f"   Time of Day: {act.time_of_day}")
        print(f"   Cost: ₹{act.cost}")
    except ValidationError as e:
        print("❌ Activity Validation Failed:", e)

    print("\n==================================================")
    print("2. TEST: Standalone DayPlan with Multiple Activities")
    print("==================================================")
    dayplan_dict = {
        "date": "2026-10-10",
        "weather_summary": "Partly cloudy, 28°C",
        "activities": [
            {
                "time_of_day": "morning",
                "name": "Amber Fort Tour",
                "description": "Guided walking tour",
                "cost": 500.0,
            },
            {
                "time_of_day": "afternoon",
                "name": "Local Bazaar Shopping",
                "description": "Shop for handicrafts and textiles at Johari Bazaar",
                "cost": 2000.0,
            },
            {
                "time_of_day": "evening",
                "name": "Chokhi Dhani Dinner",
                "description": "Traditional Rajasthani dinner and cultural performance",
                "cost": 1200.0,
            },
        ],
        "day_total_cost": 3700.0,
    }

    try:
        day_plan = DayPlan(**dayplan_dict)
        print("✅ DayPlan instantiated successfully:")
        print(f"   Date: {day_plan.date}")
        print(f"   Weather: {day_plan.weather_summary}")
        print(f"   Total Activities: {len(day_plan.activities)}")
        print(f"   Calculated Day Cost: ₹{day_plan.day_total_cost}")
    except ValidationError as e:
        print("❌ DayPlan Validation Failed:", e)

    print("\n==================================================")
    print("3. TEST: Activity Type Mismatch Error Handling")
    print("==================================================")
    invalid_activity = {
        "time_of_day": "morning",
        "name": "Scuba Diving",
        "description": "Underwater dive session",
        "cost": "free",  # Invalid float value
    }

    try:
        Activity(**invalid_activity)
    except ValidationError as e:
        print("✅ Caught expected invalid cost error:")
        for error in e.errors():
            print(f"   - Field '{error['loc'][0]}': {error['msg']}")


if __name__ == "__main__":
    run_repl_tests()
    test_activity_and_dayplan()


