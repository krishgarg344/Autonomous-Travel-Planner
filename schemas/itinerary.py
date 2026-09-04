from pydantic import BaseModel, Field


class Activity(BaseModel):
    time_of_day: str = Field(..., description="morning, afternoon, evening, or night")
    name: str
    description: str


class DayPlan(BaseModel):
    date: str
    weather_summary: str
    activities: list[Activity]


class Itinerary(BaseModel):
    destination_city: str
    start_date: str
    end_date: str
    days: list[DayPlan]