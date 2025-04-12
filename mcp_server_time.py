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
