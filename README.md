# Autonomous-Travel-Planner

This is an Agentic AI platform that automates your trip planning. It brings the long and tiring task of surfing through many websites whether for looking for places to stay, activities to do, cafes hotels, scenic points, weather conditions etc. to just one prompt.
It gives you personalized tailored response according to your schedule and your budget requirements.

## Schemas

specifies the input and output formats for a structured data flow with LLMs and smooth data delivery

## Tools

- **`get_weather`:** Accumulates weather details using each day's temperature, precipitation chances into account. Uses free open-meteo api for fetching data
- **`get_places`:** Calls Google Places API (New) to fetch up to 10 places matching a city and user interests. Returns each place's name, address, rating, and price level when available.
- **`get_flights`:** Calls AeroDataBox API via Rapid API to get flights on a particular date from origin i.e. departure location to destination location. Returns flight details(flight no., airline, carrier, departure airport, arrival airpot, departure, arrival, status) for max upto 10 flights between origin and destination location. Doesnt include flight prices yet.