# For syntax visit -> https://docs.langchain.com/oss/python/langchain/overview

import re
from typing import Optional, List

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, before_model, ModelRequest
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from tools import All_Tools
from schemas.itinerary import Itinerary
import config


# ---------------- TripState ----------------
class TripState(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    interests: List[str] = []

    def update_from(self, changes: dict):
        for key, value in changes.items():
            if value:
                setattr(self, key, value)

    def is_ready_for_tools(self) -> bool:
        return all([self.origin, self.destination, self.departure_date])


# ---------------- TripState store (session-scoped, app-level, not LLM messages) ----------------
_trip_states: dict[str, TripState] = {}

def get_trip_state(session_id: str) -> TripState:
    if session_id not in _trip_states:
        _trip_states[session_id] = TripState()
    return _trip_states[session_id]


# ---------------- TripState extraction (naive, application-side, not an LLM tool) ----------------
ACTION_VERBS = {"leave", "go", "fly", "travel", "depart", "return", "visit", "head", "get", "plan"}

def extract_trip_updates(user_message: str) -> dict:
    msg = user_message.strip()
    changes = {}

    # Origin: "from Delhi", "travelling from Delhi"
    from_match = re.search(
        r"\bfrom\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\b",
        msg,
        re.IGNORECASE
    )
    if from_match:
        origin_val = from_match.group(1).strip().title()
        if origin_val.lower() not in {"here", "there", "home"}:
            changes["origin"] = origin_val

    # Destination: "to Goa", "trip to Goa", avoiding verbs like "to leave" or "to plan"
    to_matches = re.finditer(
        r"\bto\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\b",
        msg,
        re.IGNORECASE
    )
    for match in to_matches:
        candidate = match.group(1).strip().title()
        first_word = candidate.split()[0].lower()
        if first_word not in ACTION_VERBS:
            changes["destination"] = candidate
            break

    # Departure date: "leave on 2026-09-15"
    departure_match = re.search(
        r"(?:leave|depart|departure)\s+(?:on|date\s+is)?\s*(\d{4}-\d{2}-\d{2})",
        msg,
        re.IGNORECASE
    )
    if departure_match:
        changes["departure_date"] = departure_match.group(1)

    # Return date: "return on 2026-09-20"
    return_match = re.search(
        r"(?:return|come\s+back)\s+(?:on|date\s+is)?\s*(\d{4}-\d{2}-\d{2})",
        msg,
        re.IGNORECASE
    )
    if return_match:
        changes["return_date"] = return_match.group(1)

    # Interests: stop at punctuation or common connecting conjunctions
    interest_match = re.search(
        r"(?:interested\s+in|i\s+like|interests?\s+(?:are|include))\s+([^.\n]+)",
        msg,
        re.IGNORECASE
    )
    if interest_match:
        interests_text = interest_match.group(1)
        interests = re.split(r",|\band\b", interests_text, flags=re.IGNORECASE)

        cleaned = []
        for interest in interests:
            item = interest.strip().lower()
            if item:
                cleaned.append(item)

        if cleaned:
            changes["interests"] = cleaned

    return changes

def apply_trip_updates(session_id: str, user_message: str):
    trip_state = get_trip_state(session_id)
    changes = extract_trip_updates(user_message)
    trip_state.update_from(changes)


# ---------------- System prompt ----------------
SYSTEM_PROMPT_TEMPLATE = """
You are a travel planning assistant. Gather trip details, call tools
only when necessary, and produce a plain-text draft itinerary.

CURRENT TRIP STATE:
{trip_state_json}

RULES:
1. TripState is the source of truth. Don't ask for info already present.
2. If origin, destination, or dates are missing, ask for them before
   calling get_flights, get_weather, or get_places.
3. Don't call the same tool again for the same route/date/location
   unless the request has changed.
4. get_flights returns schedules only — never state a price.
5. If a tool errors or returns nothing, acknowledge it briefly and move
   on without retrying.
6. get_places returns limited results — choose from them rather than
   re-calling unless preferences clearly aren't met.
7. Never invent facts not returned by a tool.
8. Once enough information is gathered, produce a plain-text
   day-by-day draft itinerary. Do not output JSON yourself.
"""


# ---------------- Custom agent state (adds trip_state_json to AgentState) ----------------
class TravelAgentState(AgentState):
    trip_state_json: str


# ---------------- Middleware: inject TripState into system prompt each call ----------------
@dynamic_prompt
def inject_trip_state(request: ModelRequest) -> str:
    trip_json = request.state.get("trip_state_json", "{}")
    return SYSTEM_PROMPT_TEMPLATE.format(trip_state_json=trip_json)


# ---------------- Middleware: bound conversation history ----------------
MAX_MESSAGES = 12  # ~6 turns

@before_model
def trim_messages(state: TravelAgentState, runtime: Runtime):
    messages = state["messages"]
    if len(messages) <= MAX_MESSAGES:
        return None
    trimmed = messages[-MAX_MESSAGES:]
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *trimmed]}


# ---------------- Build the agent (Groq, tool-calling, memory via checkpointer) ----------------
checkpointer = InMemorySaver()

agent = create_agent(
    model=config.GROQ_MODEL,          # e.g. "groq:llama-3.3-70b-versatile"
    tools=All_Tools,
    state_schema=TravelAgentState,
    middleware=[inject_trip_state, trim_messages],
    checkpointer=checkpointer,
)


# ---------------- Gemini structured-output formatter (no tools, separate step) ----------------
def format_itinerary(draft_text: str, trip_state: TripState) -> Itinerary:
    gemini = ChatGoogleGenerativeAI(model=config.GEMINI_MODEL, temperature=0)
    structured_llm = gemini.with_structured_output(Itinerary)
    return structured_llm.invoke(
        f"Trip details: {trip_state.model_dump_json()}\n\n"
        f"Draft itinerary:\n{draft_text}\n\n"
        f"Convert this into the structured Itinerary format."
    )


# ---------------- Entry point ----------------
def handle_user_message(session_id: str, user_message: str):
    apply_trip_updates(session_id, user_message)
    trip_state = get_trip_state(session_id)

    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": user_message}],
            "trip_state_json": trip_state.model_dump_json(),
        },
        config={"configurable": {"thread_id": session_id}},
    )

    draft_text = result["messages"][-1].content

    if trip_state.is_ready_for_tools():
        return format_itinerary(draft_text, trip_state)
    return draft_text