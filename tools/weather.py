"""Example tool: get current weather for a city."""

from agents import function_tool


@function_tool
def get_weather(city: str, units: str = "celsius") -> str:
    """Get current weather for a location. Replace with a real API call."""
    temp = 22 if units == "celsius" else 72
    return f"{city}: {temp}°{'C' if units == 'celsius' else 'F'}, partly cloudy"
