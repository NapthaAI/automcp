import warnings
from typing import Any
from automcp.adapters.pydantic_adapter import create_pydantic_agent_adapter
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("MCP Server")

# Suppress warnings that might interfere with STDIO transport
warnings.filterwarnings("ignore")

from main import weather_agent

# Define the input schema for your crew
class InputSchema(BaseModel):
    query: str

name = "weather_agent"
description = "Get the weather in a location"

# Create an adapter for Langchain
mcp_pydantic_agent = create_pydantic_agent_adapter(
    agent_instance=weather_agent,
    name=name,
    description=description,
    input_schema=InputSchema,
)

mcp.add_tool(
    mcp_pydantic_agent,
    name=name,
    description=description
)

# Server entrypoints
def serve_sse():
    mcp.run(transport="sse")

def serve_stdio():
    # Redirect stderr to suppress warnings that bypass the filters
    import os
    import sys

    class NullWriter:
        def write(self, *args, **kwargs):
            pass
        def flush(self, *args, **kwargs):
            pass

    # Save the original stderr
    original_stderr = sys.stderr

    # Replace stderr with our null writer to prevent warnings from corrupting STDIO
    sys.stderr = NullWriter()

    # Set environment variable to ignore Python warnings
    os.environ["PYTHONWARNINGS"] = "ignore"

    try:
        mcp.run(transport="stdio")
    finally:
        # Restore stderr for normal operation
        sys.stderr = original_stderr

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        serve_sse()
    else:
        serve_stdio() 