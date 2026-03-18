from mcp.server.fastmcp import FastMCP

from constants import NWS_API_BASE
from utils import make_nws_request, format_alert


mcp = FastMCP("weather")


@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Get weather alerts for a US state. Do NOT use this tool for international locations outside the US.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """

    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Get weather forecast for a location within the United States. Do NOT use this tool for international locations outside the US

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return (
            "Error: This location appears to be outside the supported US grid. "
            "Please explicitly tell the user that you cannot fetch real-time weather "
            "for international locations, and then provide the typical seasonal climate "
            "for this area based on your general knowledge."
        )

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Error: Unable to fetch detailed forecast from the NWS API. Please inform the user."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
        {period["name"]}:
        Temperature: {period["temperature"]}°{period["temperatureUnit"]}
        Wind: {period["windSpeed"]} {period["windDirection"]}
        Forecast: {period["detailedForecast"]}
        """
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    mcp.run(transport="stdio")
