# streamlit_app.py

import uuid
from datetime import datetime

import streamlit as st

import requests
from schemas.itinerary import Itinerary


API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="AI Travel Planner", layout="centered")

st.title("AI Travel Planner")
st.caption(
    "Tell me your origin, destination, travel dates, and interests — "
    "I'll plan your trip using live weather, flight, and places data."
)

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str}]

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None


def format_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return date_str


def render_itinerary_markdown(itinerary: Itinerary) -> str:
    lines = [
        f"### Trip to {itinerary.destination_city}",
        f"**{format_date(itinerary.start_date)} – {format_date(itinerary.end_date)}**",
        "",
    ]

    for i, day in enumerate(itinerary.days, start=1):
        lines.append(f"#### Day {i} — {format_date(day.date)}")
        if day.weather_summary:
            lines.append(f"*Weather: {day.weather_summary}*")

        for activity in day.activities:
            label = activity.time_of_day.strip().capitalize()
            lines.append(f"- **{label}:** {activity.name} — {activity.description}")

        lines.append("")
        lines.append("---")

    return "\n".join(lines)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if st.session_state.itinerary is not None:
    st.divider()
    st.subheader("Your Itinerary")
    st.markdown(render_itinerary_markdown(st.session_state.itinerary))
    st.divider()


user_input = st.chat_input("Tell me about your trip...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/trip/chat",
                    json={
                        "session_id": st.session_state.session_id,
                        "message": user_input,
                    },
                )

                response.raise_for_status()
                data = response.json()

                if data["type"] == "itinerary":
                    result = Itinerary.model_validate(data["itinerary"])
                else:
                    result = data["message"]

            except Exception as e:
                result = f"Something went wrong: {e}"

        if isinstance(result, Itinerary):
            st.session_state.itinerary = result
            reply_text = "Your itinerary is ready — see below."
        else:
            reply_text = result

        st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})

    if st.session_state.itinerary is not None:
        st.rerun()