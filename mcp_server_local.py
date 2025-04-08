from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Weather",
    instructions="You are a weather assistant that can answer questions about the weather in a given location.",
    host="0.0.0.0",
    port=8005,
)


@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get current weather information for the specified location.

    This function simulates a weather service by returning a fixed response.
    In a production environment, this would connect to a real weather API.

    Args:
        location (str): The name of the location (city, region, etc.) to get weather for

    Returns:
        str: A string containing the weather information for the specified location
    """
    return f"It's always Sunny in {location}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
