from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz
from typing import Optional

mcp = FastMCP(
    "TimeService",
    instructions="You are a time assistant that can provide the current time for different timezones.", 
    host="0.0.0.0",
    port=8005,
)


@mcp.tool()
async def get_current_time(timezone: Optional[str] = "Asia/Seoul") -> str:
    """
    Get current time information for the specified timezone.

    This function returns the current system time for the requested timezone.

    Args:
        timezone (str, optional): The timezone to get current time for. Defaults to "Asia/Seoul".

    Returns:
        str: A string containing the current time information for the specified timezone
    """
    try:
        tz = pytz.timezone(timezone)

        current_time = datetime.now(tz)

        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")

        return f"Current time in {timezone} is: {formatted_time}"
    except pytz.exceptions.UnknownTimeZoneError:
        return f"Error: Unknown timezone '{timezone}'. Please provide a valid timezone."
    except Exception as e:
        return f"Error getting time: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
