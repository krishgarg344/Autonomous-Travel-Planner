from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    origin_city: str = Field(..., description="City the traveler is departing from")
    destination_city: str = Field(..., description="City being visited")
    start_date: str = Field(..., description="Trip start date, YYYY-MM-DD")
    end_date: str = Field(..., description="Trip end date, YYYY-MM-DD")
    interests: str = Field(..., description="Comma separated interests, e.g. 'beaches, food, nightlife'")
    travelers: int = Field(default=1, description="Number of people traveling")
