# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import handle_user_message, get_trip_state
from schemas.request import TripRequest
from schemas.itinerary import Itinerary

app = FastAPI(title="AI Travel Planner")


class StartTripRequest(BaseModel):
    session_id: str
    trip: TripRequest

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/trip/start")
def start_trip(payload: StartTripRequest):
    trip_state = get_trip_state(payload.session_id)
    trip_state.update_from(payload.trip.model_dump())

    try:
        result = handle_user_message(payload.session_id, "Please plan this trip.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return _format_result(payload.session_id, result)


@app.post("/trip/chat")
def chat(payload: ChatRequest):
    try:
        result = handle_user_message(payload.session_id, payload.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return _format_result(payload.session_id, result)


def _format_result(session_id: str, result):
    if isinstance(result, Itinerary):
        return {
            "session_id": session_id,
            "type": "itinerary",
            "itinerary": result.model_dump(),
        }
    return {
        "session_id": session_id,
        "type": "draft",
        "message": result,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)