from pydantic import BaseModel, Field


class Activity(BaseModel):
    time_of_day: str = Field(..., description="morning, afternoon, evening, or night")
    name: str
    description: str
    cost: float = Field(..., description="Estimated cost in INR, 0 if free")


class DayPlan(BaseModel):
    date: str
    weather_summary: str
    activities: list[Activity]
    day_total_cost: float


class Itinerary(BaseModel):
    destination_city: str
    start_date: str
    end_date: str
    flight_cost: float
    total_cost: float
    total_budget: float
    days: list[DayPlan]
    notes: str = Field(default="", description="Any budget trade-offs or warnings for the traveler")
