from agent import handle_user_message, get_trip_state

SESSION_ID = "test-session-1"

def run_test(message):
    print("\n" + "=" * 60)
    print("USER:", message)

    try:
        response = handle_user_message(SESSION_ID, message)

        print("\nAGENT:")
        print(response)

        print("\nTRIP STATE:")
        print(get_trip_state(SESSION_ID).model_dump())

    except Exception as e:
        print("\nERROR:")
        print(type(e).__name__, ":", e)


if __name__ == "__main__":
    run_test("I want to plan a trip to Goa")
    run_test("I am travelling from Delhi")
    run_test("I want to leave on 2026-09-15 and return on 2026-09-20")
    run_test("I like beaches, food and nightlife")